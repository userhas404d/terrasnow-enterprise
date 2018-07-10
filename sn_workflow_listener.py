"""Performs actions based on ServiceNow workflow inputs."""

import logging as log
import urllib

import handlers.aws_assume_role as aws_assume_role
import handlers.config as config
import handlers.git_handler as git_handler
import handlers.tfe_handler as tfe_handler
import handlers.tfe_run_handler as tfe_run_handler
import handlers.tfe_var_handler as tfe_var_handler
import handlers.tfe_workspace_handler as tfe_workspace_handler
from glom import glom

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='terrasnow_enterprise.log', level=log.INFO,
                format=FORMAT)


# TFE workspace

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
        return (
          tfe_workspace_handler.create_workspace(region=region,
                                                 org_name=org_name,
                                                 workspace_name=workspace_name,
                                                 repo_id=repo_id,
                                                 repo_version=repo_version)
                                                 )
    elif action == 'DELETE':
        log.debug('Recieved workspace DELETE event.')
        return tfe_workspace_handler.delete_workspace(region, workspace_name)
    else:
        return 'ERROR: workspace action not specified.'


def response_handler(record):
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


# TFE runs

def TFE_run_listener(request):
    """Process TFE Run requests."""
    project_name = glom(request, 'data.0.project_name', default=False).replace(
      '/', '-')
    repo_url = glom(request, 'data.0.repo_url', default=False)
    branch = glom(request, 'data.0.module_version', default=False)
    workspace_id = glom(request, 'data.0.workspace_id', default=False)
    region = glom(request, 'data.0.region', default=False)
    # get the configuraiton version upload url
    upload_url = (
      tfe_run_handler.get_upload_url(region, workspace_id))
    log.info('configuration version response: {}'.format(upload_url))
    # download the source module
    git_handler.clone_repo(repo_url, project_name, branch)
    # zip the module
    # adding extra steps wenbhook side (clone then zip vice just download the
    # 'pre-zipped' repo) to avoid having to work with gitlab api tokens
    tar_path = git_handler.file_check(
      git_handler.compress_project(project_name))
    response = tfe_run_handler.upload_configuration_files(upload_url,
                                                          tar_path)
    git_handler.cleanup(project_name)
    if not response:
        response = '{"Status": "SUCCESS"}'
    return response


# TFE variables

def variables_event_listener(request):
    """Process workflow request."""
    region = glom(request, 'data.0.region', default=False)
    cat_vars = glom(request, 'data.0.cat_vars.0', default=False)
    org_name = glom(request, 'data.0.org_name', default=False)
    workspace_id = glom(request, 'data.0.workspace_id', default=False)
    role = glom(request, 'data.0.role', default=False)
    return populate_tfe_vars(region, cat_vars, org_name, workspace_id, role)


def populate_tfe_vars(region, cat_vars, org_name, workspace_id, role):
    """Create TFE vars and return results."""
    result = []
    create_tf_vars_response = {}
    create_env_vars_response = {}
    create_tf_vars_response['tf_vars'] = (
      create_tfe_tf_vars(region, cat_vars, org_name, workspace_id))
    create_env_vars_response['env_vars'] = (
      create_tfe_env_vars(region, role, org_name, workspace_id))
    result.append(create_tf_vars_response)
    result.append(create_env_vars_response)
    log.info('returning result: {}'.format(result))
    return result


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


def create_tfe_tf_vars(region, json_obj, org, workspace_id):
    """Populate TFE vars with raw var data."""
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       region)
    conf = configFromS3.config
    raw_vars = parse_vars(json_obj)
    response = {}
    if raw_vars:
        for var in raw_vars:
            new_var = tfe_var_handler.TFEVars(var, raw_vars[var], org=org,
                                              workspace_id=workspace_id
                                              ).get_var()
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


# AWS assume role

def assume_role_listener(request):
    """Process assume role request."""
    log.debug('Recieved assume role request: {}'.format(request))
    region = glom(request, 'data.0.region', default=False)
    org_name = glom(request, 'data.0.org_name', default=False)
    workspace_id = glom(request, 'data.0.workspace_id', default=False)
    role = glom(request, 'data.0.assume_role.0.role', default=False)
    duration = 900
    temp_creds = aws_assume_role.get_assumed_role_credentials(role, duration)
    aws_access_key_id = glom(temp_creds, 'aws_access_key_id', default=False)
    if aws_access_key_id:
        return create_cred_env_vars(region, workspace_id, org_name,
                                    temp_creds)
    else:
        log.error("Assume role request failed: {}".format(temp_creds))
        return "ERROR: Assume role request failed"


def create_tfe_env_vars(region, role, org_name, workspace_id):
    """Create TFE envirornment variables."""
    log.debug('Creating tfe env vars.')
    duration = 7200
    temp_creds = aws_assume_role.get_assumed_role_credentials(role, duration)
    aws_access_key_id = glom(temp_creds, 'aws_access_key_id', default=False)
    if aws_access_key_id:
        return create_cred_env_vars(region, workspace_id, org_name,
                                    temp_creds)
    else:
        log.error("Assume role request failed: {}".format(temp_creds))
        return "ERROR: Assume role request failed"


def create_cred_env_vars(region, workspace_id, org, temp_creds):
    """Create TFE Credential Environment Variables."""
    # pull the configuration
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       region)
    conf = configFromS3.config
    # get properly formatted json objs for variable creation
    access_key_id = create_access_key_id_var(
      glom(temp_creds, 'aws_access_key_id', default=False),
      workspace_id, org)
    secret_access_key = create_secret_access_key_id_var(
      glom(temp_creds, 'aws_secret_access_key', default=False),
      workspace_id, org)
    aws_session_token = create_session_token_var(
      glom(temp_creds, 'aws_session_token', default=False),
      workspace_id, org)
    tfe_region = create_region_var(region, workspace_id, org)
    # check to see if the temp creds exist
    if access_key_id and secret_access_key:
        api_endpoint = "/vars"
        response = {}
        # create the access key id tfe env var
        record = (
          tfe_handler.TFERequest(api_endpoint, access_key_id, conf))
        response['access_key_id'] = record.make_request()
        # create the secret access key tfe env var
        record = (
          tfe_handler.TFERequest(api_endpoint, secret_access_key, conf))
        response['secret_access_key'] = record.make_request()
        # create the region tfe env var
        # hardcoding this for now
        record = (
          tfe_handler.TFERequest(api_endpoint, tfe_region, conf))
        response['region'] = record.make_request()
        # create the aws session token env var
        record = (
          tfe_handler.TFERequest(api_endpoint, aws_session_token, conf))
        response['aws_session_token'] = record.make_request()
        log.debug('Create tfe_var response: {}'.format(response))
        return response
    else:
        log.error("Access Key Id or Secret Access Key not found.")
        return "ERROR: Access Key Id or Secret Access Key not found"


def create_access_key_id_var(access_key_id, workspace_id, org):
    """Return env var object."""
    if access_key_id:
        return tfe_var_handler.TFEVars(key="AWS_ACCESS_KEY_ID",
                                       value=access_key_id,
                                       category='env',
                                       org=org,
                                       workspace_id=workspace_id).get_var()
    else:
        log.error("Access Key Id not found.")
        return False


def create_secret_access_key_id_var(secret_access_key, workspace_id, org):
    """Return env var object."""
    if secret_access_key:
        return tfe_var_handler.TFEVars(key="AWS_SECRET_ACCESS_KEY",
                                       value=secret_access_key,
                                       category='env',
                                       org=org,
                                       workspace_id=workspace_id,
                                       is_senative=True).get_var()
    else:
        log.error("Secret Access Key not found.")
        return False


def create_region_var(region, workspace_id, org):
    """Return the region env var object."""
    return tfe_var_handler.TFEVars(key="AWS_DEFAULT_REGION",
                                   value=region,
                                   category='env',
                                   org=org,
                                   workspace_id=workspace_id).get_var()


def create_session_token_var(aws_session_token, workspace_id, org):
    """Return the session token evn var object."""
    return tfe_var_handler.TFEVars(key="AWS_SESSION_TOKEN",
                                   value=aws_session_token,
                                   category='env',
                                   org=org,
                                   workspace_id=workspace_id).get_var()
