"""Handle client script creations."""

import logging
import os


class SnowClientScript(object):
    """Servicenow client script."""

    def __init__(self, cat_item_id):
        """Initialize."""
        self.cat_item_id = cat_item_id
        self.client_script_list = []
        self.sn_javascript_path = '/sn_javascript/'

    def getJavascriptText(self, target_file):
        """Return text of the target file."""
        try:
            jspath = os.getcwd() + self.sn_javascript_path
            with open(jspath + '/' + target_file) as file:
                script_text = file.read()
            return script_text
        except FileNotFoundError as e:
            logging.exception('File not found')
            print('ERROR')
            raise

    def create_client_script(self, name, script_type, cat_var, script):
        """Create client script data block from REST call."""
        self.client_script_list.append(
             {
                 "active": "true",
                 "name": name,
                 "applies_to": "A Catalog item",
                 "ui_type": "0",
                 "type": script_type,  # onChange, onLoad, onUpdate
                 "cat_item": self.cat_item_id,
                 "cat_variable": cat_var,
                 "applies_catalog": "true",
                 "applies_sc_task": "true",
                 "script": script
             })

    def create_display_toggle(self):
        """Create the dispaly toggle client script."""
        self.create_client_script(name="display toggle",
                                  script_type="onChange",
                                  cat_var="adv_toggle",
                                  script=self.getJavascriptText(
                                   'createDisplayToggleOnload.js'))

    def create_hide_generic_vars(self):
        """Create the dispaly toggle client script."""
        self.create_client_script(name="hide generic vars",
                                  script_type="onLoad",
                                  cat_var="",
                                  script=self.getJavascriptText(
                                    'hideGenericVariablesOnLoad.js'))

    def create_population_dropdown(self):
        """Create the dispaly toggle client script."""
        self.create_client_script(name="populate dropdowns",
                                  script_type="onLoad",
                                  cat_var="",
                                  script=self.getJavascriptText(
                                    'populateDropdownsOnLoad.js'))

    def create_subnet_filter(self):
        """Create the dispaly toggle client script."""
        self.create_client_script(name="subnet filter",
                                  script_type="onChange",
                                  cat_var="tfv_SecurityGroupIds",
                                  script=self.getJavascriptText(
                                    'filterSubnetsOnChange.js'))

    def get_scripts(self):
        """Preform correct order of operations and return variables."""
        self.create_display_toggle()
        self.create_hide_generic_vars()
        self.create_population_dropdown()
        self.create_subnet_filter()
        return self.client_script_list
