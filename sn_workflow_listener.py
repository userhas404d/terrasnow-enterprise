"""Performs actions based on ServiceNow workflow inputs."""

import logging as log
import urllib

import handlers.config as config
import handlers.tfe_handler as tfe_handler
import handlers.tfe_var_handler as tfe_var_handler
import handlers.tfe_workspace_handler as tfe_workspace_handler
from glom import glom

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='snowgetter.log', level=log.INFO, format=FORMAT)

# workspace


def workspace_event_listener(request):
    """Process workflow request."""
    log.debug('workspace event: {} recieved'.format(request))
    region = glom(request, 'data.0.region', default=False)
    org_name = glom(request, 'data.0.org_name', default=False)
    workspace_name = glom(request, 'data.0.workspace_name', default=False)
    repo_id = glom(request, 'data.0.repo_id', default=False)
    repo_version = glom(request, 'data.0.repo_version', default=False)
    action = glom(request, 'data.0.action', default=False)
    if action == 'CREATE':
        log.debug('Recieved workspace CREATE event.')
        return create_workspace(region, org_name, workspace_name, repo_id,
                                repo_version)
    elif action == 'DELETE':
        log.debug('Recieved workspace DELETE event.')
        return delete_workspace(region, org_name, workspace_name)
    else:
        return 'ERROR: workspace action not specified.'


def create_workspace(region, org_name, workspace_name, repo_id, repo_version):
    """Create TFE workspace."""
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       region)
    conf = configFromS3.config
    w = tfe_workspace_handler.TFEWorkspace(name=workspace_name,
                                           vcs_repo_id=repo_id,
                                           vcs_repo_branch=repo_version,
                                           oauth_token_id=(
                                             tfe_handler.get_vcs_oauth(conf)))
    workspace = w.get_workspace()
    api_endpoint = "/organizations/{}/workspaces".format(org_name)
    record = tfe_handler.TFERequest(api_endpoint, workspace, conf)
    return response_hanlder(record)


def delete_workspace(region, org_name, workspace_name):
    """Delete TFE workspace."""
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       region)
    conf = configFromS3.config
    api_endpoint = "/organizations/{}/workspaces/{}".format(org_name,
                                                            workspace_name)
    record = tfe_handler.TFERequest(api_endpoint, None, conf)
    response = record.delete()
    log.debug('Delete TFE workspace response: {}'.format(response))
    return response


def response_hanlder(record):
    """Evaulate response."""
    try:
        response = record.make_request()
        log.debug('Create TFE workspace response: {}'.format(response))
        return response
    except urllib.error.HTTPError as e:
        if e.code == 422:
            return "ERROR: Worspace already exists"
        else:
            return "ERROR"

# variables


def variables_event_listener(request):
    """Process workflow request."""
    region = glom(request, 'data.0.region', default=False)
    cat_vars = glom(request, 'data.0.cat_vars.0', default=False)
    org_name = glom(request, 'data.0.org_name', default=False)
    workspace_name = glom(request, 'data.0.workspace_name', default=False)
    return create_vars(region, cat_vars, org_name, workspace_name)


def remove_prefix(text, prefix):
    """Remove string prefix."""
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def parse_vars(json_obj):
    """Convert SN variables to terraform variables."""
    raw_vars = {}
    # 1. remove unnecessary vars (gen_)
    for var in json_obj:
        if var.startswith('tfv_'):
            rm_prefix = remove_prefix(var, 'tfv_')
            raw_vars[rm_prefix] = json_obj[var]
    return raw_vars


def create_vars(region, json_obj, org, workspace):
    """Populate TFE vars with raw var data."""
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       region)
    conf = configFromS3.config
    raw_vars = parse_vars(json_obj)
    response = {}
    if raw_vars:
        for var in raw_vars:
            new_var = tfe_var_handler.TFEVars(var, raw_vars[var], org=org,
                                              workspace=workspace).get_var()
            print("var payload: {}".format(new_var))
            api_endpoint = "/vars"
            record = tfe_handler.TFERequest(api_endpoint, new_var, conf)
            var_response = record.make_request()
            log.debug('Create tfe_var response: {}'.format(response))
            response[var] = var_response
        return response
    else:
        log.error("Input json object was empty.")
        return "ERROR: vars json object cannot be empty"
