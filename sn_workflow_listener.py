"""Performs actions based on ServiceNow workflow inputs."""

import logging as log
import urllib

import handlers.aws_assume_role as aws_assume_role
import handlers.config as config
import handlers.tfe_handler as tfe_handler
import handlers.tfe_var_handler as tfe_var_handler
import handlers.tfe_workspace_handler as tfe_workspace_handler
from glom import glom

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='terrasnow_enterprise.log', level=log.INFO,
                format=FORMAT)

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


# assume role

def assume_role_listener(request):
    """Process assume role request."""
    log.debug('Recieved assume role request: {}'.format(request))
    region = glom(request, 'data.0.region', default=False)
    org_name = glom(request, 'data.0.org_name', default=False)
    workspace_name = glom(request, 'data.0.workspace_name', default=False)
    role = glom(request, 'data.0.assume_role.0.role', default=False)
    duration = 900
    temp_creds = aws_assume_role.get_assumed_role_credentials(role, duration)
    aws_access_key_id = glom(temp_creds, 'aws_access_key_id', default=False)
    if aws_access_key_id:
        return create_env_vars(region, workspace_name, org_name, temp_creds)
    else:
        log.error("Assume role request failed: {}".format(temp_creds))
        return "ERROR: Assume role request failed"


def create_env_vars(region, workspace, org, temp_creds):
    """Create TFE Credential Environment Variables."""
    # pull the configuration
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       region)
    conf = configFromS3.config
    # get properly formatted json objs for variable creation
    access_key_id = create_access_key_id_var(
      glom(temp_creds, 'aws_access_key_id', default=False),
      workspace, org)
    secret_access_key = create_secret_access_key_id_var(
      glom(temp_creds, 'aws_secret_access_key', default=False),
      workspace, org)
    # check to see if the temp creds exist
    if access_key_id and secret_access_key:
        api_endpoint = "/vars"
        response = {}
        record = (
          tfe_handler.TFERequest(api_endpoint, access_key_id, conf))
        response['access_key_id'] = record.make_request()
        record = (
          tfe_handler.TFERequest(api_endpoint, secret_access_key, conf))
        response['secret_access_key'] = record.make_request()
        log.debug('Create tfe_var response: {}'.format(response))
        return response
    else:
        log.error("Access Key Id or Secret Access Key not found.")
        return "ERROR: Access Key Id or Secret Access Key not found"


def create_access_key_id_var(access_key_id, workspace, org):
    """Return env var object."""
    if access_key_id:
        return tfe_var_handler.TFEVars(key="AWS_ACCESS_KEY_ID",
                                       value=access_key_id,
                                       category='env',
                                       org=org,
                                       workspace=workspace).get_var()
    else:
        log.error("Access Key Id not found.")
        return False


def create_secret_access_key_id_var(secret_access_key, workspace, org):
    """Return env var object."""
    if secret_access_key:
        return tfe_var_handler.TFEVars(key="AWS_SECRET_ACCESS_KEY",
                                       value=secret_access_key,
                                       category='env',
                                       org=org,
                                       workspace=workspace,
                                       is_senative=True).get_var()
    else:
        log.error("Secret Access Key not found.")
        return False
