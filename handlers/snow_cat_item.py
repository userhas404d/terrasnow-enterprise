"""Define Snow Category Item."""

import logging


class SnowCatalogItem(object):
    """ServiceNow Category Item."""

    def __init__(self, name, description, conf):
        """Initialize."""
        self.name = name
        # terraform catalog sys_id
        self.catalog = conf.get("SERVICENOW", "TF_CATALOG")
        # terraform catalog's watchmaker category
        self.category = conf.get("SERVICENOW", "CATEGORY")
        self.description = description
        # terraform deployment workflow
        self.workflow = conf.get("SERVICENOW", "TFE_WORKFLOW")
        self.isactive = "true"

    def data(self):
        """Create category item data payload."""
        logging.info('')
        return {"name": self.name,
                "category": self.category,
                "sc_catalogs": self.catalog,
                "short_description": self.description,
                "workflow": self.workflow,
                "active": self.isactive
                }
