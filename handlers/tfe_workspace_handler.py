"""Class to define a terraform enterprise workspace."""
# https://www.terraform.io/docs/enterprise/api/workspaces.html

import logging as log
import urllib.parse
import urllib.request

import handlers.config as config
import handlers.tfe_handler as tfe_handler
from glom import glom


class TFEWorkspace(object):
    """Terraform Enterprise Workspace."""

    def __init__(self, name, vcs_repo_id, oauth_token_id, tf_version="0.11.1",
                 working_dir="", vcs_repo_branch=""):
        """Initialize."""
        self.name = name
        self.tf_version = tf_version
        self.working_dir = working_dir
        self.vcs_repo_id = vcs_repo_id
        self.oauth_token_id = oauth_token_id
        self.vcs_repo_branch = vcs_repo_branch

    def initialize_workspace(self):
        """Return create TFE workspace request body."""
        return {
             "data": {
               "attributes": {
                 "name": self.name,
                 "auto-apply": True,
                 "terraform_version": self.tf_version,
                 "working-directory": self.working_dir,
                 "vcs-repo": {
                   "identifier": self.vcs_repo_id,
                   "oauth-token-id": self.oauth_token_id,
                   "branch": self.vcs_repo_branch,
                   "default-branch": "true"
                 }
               },
               "type": "workspaces"
             }
           }


def create_workspace(region, org_name, workspace_name, repo_id, repo_version):
    """Create TFE workspace."""
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       region)
    conf = configFromS3.config
    w = TFEWorkspace(name=workspace_name, vcs_repo_id=repo_id,
                     vcs_repo_branch=repo_version, oauth_token_id=(
                       tfe_handler.get_vcs_oauth(conf)))
    workspace = w.initialize_workspace()
    api_endpoint = "/organizations/{}/workspaces".format(org_name)
    record = tfe_handler.TFERequest(api_endpoint, workspace, conf)
    return response_handler(record)


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


def get_workspace(region, org_name, workspace_name):
    """Get the target workspace information."""
    configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                       region)
    conf = configFromS3.config
    api_endpoint = "/organizations/{}/workspaces/{}".format(org_name,
                                                            workspace_name)
    response = tfe_handler.TFERequest(api_endpoint, None, conf)
    log.debug('Get TFE workspace reponse: {}'.format(response))
    return response_handler(response)


def get_workspace_id(region, org_name, workspace_name):
    """Return the workspace id."""
    response = get_workspace(region, org_name, workspace_name)
    return glom(response, 'data.id', default=False)


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
