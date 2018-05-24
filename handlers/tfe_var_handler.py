"""Pass ServiceNow terraform vars to TFE instance."""
# https://www.terraform.io/docs/enterprise/api/variables.html


class TFEVars(object):
    """Terraform Enterprise Variables."""

    def __init__(self, key, value, org, workspace, category="terraform",
                 is_hcl="false", is_senative="false"):
        """Initialize."""
        self.key = key
        self.value = value
        self.category = category
        self.is_hcl = is_hcl
        self.is_senative = is_senative
        self.org = org
        self.workspace = workspace

    def get_var(self):
        """Return TFE var data block."""
        return {
                 "data": {
                    "type": "vars",
                    "attributes": {
                      "key": self.key,
                      "value": self.value,
                      "category": self.category,
                      "hcl": self.is_hcl,
                      "sensitive": self.is_senative
                    }
                  },
                 "filter": {
                    "organization": {
                      "name": self.org
                    },
                    "workspace": {
                      "name": self.workspace
                    }
                  }
                }
