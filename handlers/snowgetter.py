"""Get servicenow data via REST."""

# ToDo:
# configure SN api calls to use oauth
# replace sys_id_check function with glom

import ast
import json
import logging
import os
import pathlib
import urllib.parse
import urllib.request
import urllib.response

from glom import glom

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(filename='snowgetter.log', level=logging.DEBUG,
                    format=FORMAT)


class snow_record(object):
    """ServiceNow record."""

    def __init__(self, target, query, data, conf):
        """Make ServiceNow REST call."""
        self.target = target
        self.query = self.parse_query(query)
        self.user = conf.get("SERVICENOW", "SN_API_USER_NAME")
        self.password = conf.get("SERVICENOW", "SN_API_USER_PWD")
        self.response = None
        self.headers = {
                   "Content-Type": "application/json",
                   "Accept": "application/json"
                   }
        self.host = conf.get("SERVICENOW", "INSTANCE_NAME")
        self.base_url = 'https://{}/api/now/'.format(self.host)
        self.request_content = None
        self.data = self.parse_data(data)
        self.url = self.url()
        self.opener = self.get_opener()
        self.file_name = None
        self.file_path = None

    def parse_data(self, data):
        """Put data in correct format."""
        if data is None or data == "":
            return None
        else:
            return str.encode(json.dumps(data))

    def get_opener(self):
        """Define the authorization handler for urllib."""
        p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, self.base_url, self.user, self.password)

        auth_handler = urllib.request.HTTPBasicAuthHandler(p)
        return urllib.request.build_opener(auth_handler)

    def parse_query(self, query):
        """Convert query string to url encoded format."""
        if query is None or query == "":
            logging.info('No search query specified.')
            return None
        else:
            try:
                logging.info('Query supplied: {}'.format(query))
                query = 'sysparm_query=' + urllib.parse.quote_plus(query)
                logging.info('Query in url format: {}'.format(query))
            except TypeError as e:
                logging.exception('Query not in expected format.')
            return query

    def url(self):
        """Create the url."""
        if self.query is not None or self.query == "" and self.data is None:
            url = (self.base_url + self.target + self.query +
                   '&sysparm_limit=1')
            logging.info('Url created with query: {}'.format(url))
            return url
        elif self.data is not None or self.data != "":
            url = (self.base_url + self.target)
            logging.info('Url create for POST request.')
            return url
        else:
            url = self.base_url + self.target + '?sysparm_limit=1'
            logging.info('Url created without query: {}'.format(url))
            return url

    def make_PATCH_request(self):
        """Make a POST request."""
        try:
            urllib.request.install_opener(self.opener)
            req = urllib.request.Request(self.url,
                                         data=self.data,
                                         headers=self.headers,
                                         method='PATCH')
            self.response = self.opener.open(req)
            return self.eval_response()
        except IOError as e:
            print(e)

    def make_POST_request(self):
        """Make a POST request."""
        try:
            urllib.request.install_opener(self.opener)
            req = urllib.request.Request(self.url,
                                         data=self.data,
                                         headers=self.headers)
            self.response = self.opener.open(req)
            return self.eval_response()
        except IOError as e:
            print(e)

    def make_GET_request(self):
        """Make the GET request."""
        urllib.request.install_opener(self.opener)
        try:
            req = urllib.request.Request(self.url,
                                         data=None,
                                         headers=self.headers,
                                         method='GET')
            self.response = self.opener.open(req)
            # print(self.response.read())
            return self.eval_response()
        except IOError as e:
            print(e)

    def eval_response(self):
        """Check status of response."""
        if "/file" in self.target:
            logging.info('Returning response for file retreval.')
            return 'File retreval response'
        else:
            logging.info('Returning response for standard request.')
            self.response = self.response.read()
            self.response = self.response.decode("utf-8")
            self.response = ast.literal_eval(self.response)
            return self.response


def deactivate_cat_item(catalog_item_sys_id, sn_conf):
    """Deactivate target catalog item."""
    record = snow_record('table/sc_cat_item/{}'.format(catalog_item_sys_id),
                         "", {"active": "false"}, conf=sn_conf)
    response = record.make_PATCH_request()
    if glom(response, 'result.sys_id', default=False):
        return True
    else:
        return False


def get_sn_tf_cat_item(repo_namespace, sn_conf):
    """Return terraform catalog item sys_id given repo_namespace."""
    logging.info('submitting attachment sys_id request.')
    # query cat item vars table for specific variable (gen_repo_namespace)
    # and its default value
    query = ('cat_item.active=true'
             + '^name=gen_repo_namespace'
             + '^default_value={}'.format(repo_namespace))
    record = snow_record('table/item_option_new?', query, "", conf=sn_conf)
    logging.info('Defined snowgetter parameters.')
    response = record.make_GET_request()
    logging.info('Made get request via snowgetter.')
    logging.debug('recieved response: {}'.format(response))
    # return cat item sys_id
    return glom(response, 'result.0.cat_item.value', default=False)


def get_sn_template_version(cat_item_sys_id, sn_conf):
    """Return terraform catalog item module_version given cat item sys_id."""
    logging.info('submitting attachment sys_id request.')
    # query cat item vars table by catalog sys_id and var gen_module_version
    query = ('cat_item.active=true'
             + '^cat_item.sys_id={}'.format(cat_item_sys_id)
             + '^name=gen_module_version')
    record = snow_record('table/item_option_new?', query, "", conf=sn_conf)
    logging.info('Defined snowgetter parameters.')
    response = record.make_GET_request()
    logging.info('Made get request via snowgetter.')
    # return version number of module
    logging.debug('recieved response: {}'.format(response))
    return glom(response, 'result.0.default_value', default=False)


def get_workflow_stage(workflow_sys_id, workflow_name, stage_name, sn_conf):
    """Return name of stage."""
    logging.info('submitting workflow stage name request.')
    query = ('workflow_version.sys_id={}'.format(workflow_sys_id) +
             '^workflow_version.name={}'.format(workflow_name) +
             '^name={}'.format(stage_name))
    record = snow_record('table/wf_stage?', query, "", conf=sn_conf)
    logging.info('Defined snowgetter parameters.')
    response = record.make_GET_request()
    logging.info('Made get request via snowgetter.')
    return glom(response, 'result.0.name', default=False)


def make_cat_item(cat_item_data, sn_conf):
    """Create a category item."""
    logging.info('submitting catalog item creation request.')
    record = snow_record('table/sc_cat_item', "", cat_item_data, conf=sn_conf)
    logging.info('Defined snowgetter parameters.')
    response = record.make_POST_request()
    logging.info('Made post request via snowgetter.')
    return glom(response, 'result.sys_id', default=None)


def make_cat_var(var_item_data, sn_conf):
    """Create a category item variable."""
    logging.info('submitting catalog item creation request.')
    record = snow_record('table/item_option_new', "", var_item_data,
                         conf=sn_conf)
    logging.info('Defined snowgetter parameters.')
    response = record.make_POST_request()
    logging.info('make_cat_var request sent via snowgetter.')
    return glom(response, 'result.sys_id', default=None)


def make_client_script(client_script_data, sn_conf):
    """Create a category item variable."""
    logging.info('submitting catalog script creation request.')
    record = snow_record('table/catalog_script_client', "", client_script_data,
                         conf=sn_conf)
    logging.info('Defined snowgetter parameters.')
    response = record.make_POST_request()
    logging.info('make_client_script request sent via snowgetter.')
    return glom(response, 'result.sys_id', default=None)


def make_ssh_cred(ssh_cred_data, sn_conf):
    """Create a category item variable."""
    logging.info('submitting catalog script creation request.')
    record = snow_record('table/ssh_private_key_credentials', "",
                         ssh_cred_data, conf=sn_conf)
    logging.info('Defined snowgetter parameters.')
    response = record.make_POST_request()
    logging.info('Made post request via snowgetter.')
    return glom(response, 'result.sys_id', default=None)


def update_snow_var_value(table_name, sys_id, var_item_data, sn_conf):
    """Update values of vars in target item."""
    logging.info('submitting variable update request')
    target_record = 'table/{}/{}'.format(table_name, sys_id)
    record = snow_record(target_record, "", var_item_data, conf=sn_conf)
    logging.info('Defined snowgetter parameters.')
    response = record.make_PATCH_request()
    logging.info('Made POST request via snowgetter.')
    return response


def path_check(file_path):
    """Create the file path if it does not already exist."""
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
