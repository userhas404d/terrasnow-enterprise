"""Handle git and file based operaitons."""

import logging as log
import os
import shutil
import subprocess
import tarfile
import time
from pathlib import Path

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='terrasnow_enterprise.log', level=log.INFO,
                format=FORMAT)


def clone_repo(repo_url, project_name, branch=None):
    """Pull target gitlab repo."""
    log.debug("cloning repo: {} for project: {}".format(repo_url,
              project_name))
    project_path = "/tmp/{}".format(project_name)
    try:
        if branch:
            log.info('cloning branch: {}'.format(branch))
            cmd = ("/usr/bin/git clone --branch {} {} {}".format(branch,
                   repo_url, project_path))
            subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            log.info('cloned repo {}'.format(project_name))
        else:
            cmd = "/usr/bin/git clone {} {}".format(repo_url, project_path)
            subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            log.info('cloned repo {}'.format(project_name))
    except subprocess.CalledProcessError as e:
        log.error('git clone failed.. {}'.format(e.output))
    # check that the folder that's created contains expected files
    return project_check(project_path)


def project_check(project_path):
    """Check for required files in project folder."""
    main_tf_path = "{}/main.tf".format(project_path)
    vars_tf_path = "{}/variables.tf".format(project_path)
    main_tf_file = Path(main_tf_path)
    vars_tf_file = Path(vars_tf_path)
    # wait for required files to finish downloading
    while not (os.path.exists(main_tf_path)):
        time.sleep(1)
    if main_tf_file.is_file() and vars_tf_file.is_file():
        # return path project
        log.info('project successfully cloned to: {}'.format(project_path))
        return project_path
    else:
        log.error('Failed to clone project repo.')
        raise


def get_tf_vars_file(project_path):
    """Return tf_vars_file path object."""
    vars_tf_path = "{}/variables.tf".format(project_path)
    vars_tf_file = Path(vars_tf_path)
    return vars_tf_file


def get_tf_main_file(project_path):
    """Return main_tf_file path object."""
    main_tf_path = "{}/main.tf".format(project_path)
    main_tf_file = Path(main_tf_path)
    return main_tf_file


def compress_project(project_name):
    """Zip the project."""
    # TFE expects a tar.gz file
    log.info('compressing project: {}'.format(project_name))
    project_path = "/tmp/{}".format(project_name)
    output_file = "{}/{}.tar.gz".format(project_path, project_name)
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(project_path, arcname=os.path.sep)
    # return the tar.gz's location
    return output_file


def file_check(file_path):
    """Check for zip file."""
    while not (os.path.exists(file_path)):
        log.info('file: {} not found. Checking again..'.format(file_path))
        time.sleep(1)
    log.info('Found {}'.format(file_path))
    return file_path


def cleanup(project_name):
    """Remove the cloned repo from the local disk."""
    target_dir = "/tmp/{}".format(project_name)
    shutil.rmtree(target_dir)
    log.info('Cleanup of {} successful'.format(target_dir))
