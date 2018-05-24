"""Class to define a terraform enterprise workspace."""
# https://www.terraform.io/docs/enterprise/api/workspaces.html


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

    def get_workspace(self):
        """Return TFE workspace request body."""
        return {
             "data": {
               "attributes": {
                 "name": self.name,
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
