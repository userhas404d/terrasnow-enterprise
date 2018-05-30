"""Where the magic happens."""

import json
import logging as log
import os
import shlex
import shutil
import subprocess
import time
from pathlib import Path

import handlers.config as config
import handlers.sn_client_script_handler as sn_client_script_handler
import handlers.sn_var_handler as sn_var_handler
import handlers.snow_cat_item as snow_cat_item
import handlers.snowgetter as snowgetter
import handlers.tfe_handler as tfe_handler
import packaging
from glom import glom
from packaging.version import Version

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='snowgetter.log', level=log.DEBUG, format=FORMAT)


def get_sn_tf_cat_item(repo_namespace, sn_conf):
    """Return sys_id terraform ServiceNow catalog item."""
    return snowgetter.get_sn_tf_cat_item(repo_namespace, sn_conf)


def get_sn_template_version(cat_item_sys_id, sn_conf):
    """Return the SN template version."""
    # get_sn_template needs to return sn template json obj
    return snowgetter.get_sn_template_version(cat_item_sys_id, sn_conf)


def get_gitlab_template_version(response):
    """Return version number of gitlab template."""
    return glom(response, 'ref', default=False).replace('refs/tags/', '')


def get_gitlab_project_name(response):
    """Return gitlab project name."""
    return glom(response, 'project.name', default=False)


def get_gitlab_namespace(response):
    """Return the gitlab namespace."""
    return glom(response, 'project.path_with_namespace', default=False)


def get_repo_ssh_url(response):
    """Return the giblab repo URL."""
    return glom(response, 'project.git_ssh_url', default=False)


def clone_repo(repo_url, project_name):
    """Pull target gitlab repo."""
    project_path = "/tmp/{}".format(project_name)
    subprocess.call("git clone {} {}".format(repo_url, project_path),
                    shell=True)
    log.debug('cloned repo {}'.format(project_name))
    # check that the folder that's created contains expected files
    return project_check(project_path)


def project_check(project_path):
    """Check for required files in project folder."""
    main_tf = Path("{}/main.tf".format(project_path))
    vars_tf = Path("{}/variables.tf".format(project_path))
    # wait for required files to finish downloading
    while not (os.path.exists(main_tf) and os.path.exists(vars_tf)):
        time.sleep(1)
    if main_tf.is_file() and vars_tf.is_file():
        # return path to variables file
        return vars_tf
    else:
        log.error('Failed to clone project repo.')
        raise


def cleanup(project_name):
    """Remove the cloned repo from the local disk."""
    target_dir = "/tmp/{}".format(project_name)
    shutil.rmtree(target_dir)
    log.info('Cleanup of {} successful'.format(target_dir))


def hcl_to_json(vars_tf_path):
    """Convert HCL format files to JSON."""
    json_obj = []
    vars_tf_path = str(vars_tf_path)
    tf_loc = shlex.quote(vars_tf_path)
    cmd = 'json2hcl -reverse <' + tf_loc
    process = subprocess.run(cmd,
                             shell=True,
                             universal_newlines=True,
                             stdout=subprocess.PIPE)
    json_obj.append(json.loads(process.stdout))
    return json_obj


def create_sn_cat_item(cat_item_name, cat_item_description, sn_conf):
    """Create SN Template."""
    # define a new category item.
    my_cat = snow_cat_item.SnowCatalogItem(cat_item_name, cat_item_description)
    # create the category item and return it's sys_id
    cat_sys_id = snowgetter.make_cat_item(my_cat.data(), sn_conf)
    log.info('created catalog item: {}'.format(cat_sys_id))
    return cat_sys_id


def create_cat_item_vars(json_obj, cat_sys_id, repo_namespace, module_version,
                         sn_conf):
    """Create catalog item vars."""
    os_type = ""
    sn_vars = sn_var_handler.SnowVars(json_obj, cat_sys_id, repo_namespace,
                                      module_version, os_type)
    var_list = sn_vars.get_vars()

    # push category item variables to snow
    for item in var_list:
        snowgetter.make_cat_var(item, sn_conf)

    # create client scripts
    script_client = sn_client_script_handler.SnowClientScript(cat_sys_id)
    client_scripts = script_client.get_scripts()
    for script in client_scripts:
        snowgetter.make_client_script(script, sn_conf)


def create_sn_template(repo_url, project_name, repo_namespace, module_version,
                       cat_item_name, cat_item_description, sn_conf):
    """Create SN template."""
    vars_tf_path = clone_repo(repo_url, project_name)
    cat_sys_id = create_sn_cat_item(cat_item_name, cat_item_description)
    vars_tf_json_obj = hcl_to_json(vars_tf_path)
    create_cat_item_vars(vars_tf_json_obj, cat_sys_id, repo_namespace,
                         module_version, sn_conf)
    cleanup(project_name)


def compare_versions(sn_template_version, gitlab_template_version):
    """Compare SN and Gitlab template version numbers."""
    log.debug('sn_template_version: {}'.format(sn_template_version))
    log.debug('gitlab_template_version: {}'.format(gitlab_template_version))
    try:
        if Version(sn_template_version) < Version(gitlab_template_version):
            log.debug('sn_template_version is less than '
                      + 'gitlab_template_version')
            return True
        else:
            log.debug('sn_template_version is greater than '
                      + 'gitlab_template_version')
            return False
    except packaging.version.InvalidVersion as e:
        log.error("Invlaid version format provided:{}".format(e))
        # send email notification here


def update_sn_template(repo_url, project_name, repo_namespace, module_version,
                       cat_item_sys_id, sn_conf):
    """Update SN Template."""
    # Set existing SN template to inactive
    snowgetter.deactivate_cat_item(cat_item_sys_id, sn_conf)
    # Create new servicenow template from updated gitlab module version
    cat_item_description = "module: {} version: {}".format(
                           repo_namespace, module_version)
    create_sn_template(repo_url, project_name, repo_namespace, module_version,
                       project_name, cat_item_description)


def process_response(response):
    """Main."""
    log.debug(response)
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       "us-east-1")
    conf = configFromS3.config

    repo_namespace = get_gitlab_namespace(response)
    cat_item_sys_id = get_sn_tf_cat_item(repo_namespace, conf)

    gitlab_template_version = get_gitlab_template_version(response)
    project_name = get_gitlab_project_name(response)
    repo_url = get_repo_ssh_url(response)
    sn_template_version = get_sn_template_version(cat_item_sys_id, conf)

    if cat_item_sys_id:
        if compare_versions(sn_template_version, gitlab_template_version):
            log.info("ServiceNow terraform module update triggered")
            update_sn_template(repo_url, project_name, repo_namespace,
                               gitlab_template_version, cat_item_sys_id, conf)
            log.info("ServiceNow terraform module update complete.")
        else:
            log.info("No change in module detected.")
    else:
        log.info('Catalog item not found, creating new ServiceNow Terraform'
                 + ' module.')
        module_version = get_gitlab_template_version(response)
        cat_item_description = "module: {} version: {}".format(
                               repo_namespace, module_version)
        create_sn_template(repo_url, project_name, repo_namespace,
                           module_version, project_name, cat_item_description,
                           conf)
        log.info('New ServiceNow Terraform module created.')
        log.info('Adding module to TFE private registry.')
        tfe_handler.add_module(repo_namespace)
