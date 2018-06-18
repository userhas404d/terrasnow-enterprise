"""Calls a TFE run."""

import base64
import logging as log
import urllib.parse
import urllib.request

import handlers.config as config
import handlers.tfe_handler as tfe_handler
from glom import glom

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='terrasnow_enterprise.log', level=log.INFO,
                format=FORMAT)

# - 1. get workspace id: > going to be extracted sn side
# https://www.terraform.io/docs/enterprise/api/workspaces.html#show-workspace
# - 2. make configuration version request
# - 3. git clone template
# - 4. zip template and push it to the workspace

# Zip the module
# -1. pull the project down from github to the local host
# (git clone specific version)
# -2. while loop to check that the file has finished downloading
# -3. once file is done downloading send it's path to the upload function

# Upload the file
# 1. get correct url
#   a. query the workspace for the workspace id
#   b. with the workspace id query for the target url
# 2. upload the file and log the results

# TFE configuraiton version


def create_config_version(region, workspace_id):
    """Create workspace configuration version."""
    # https://www.terraform.io/docs/enterprise/api/configuration-versions.html#create-a-configuration-version
    if workspace_id:
        configFromS3 = config.ConfigFromS3("tfsh-config", "config.ini",
                                           region)
        conf = configFromS3.config
        api_endpoint = (
          '/workspaces/{}/configuration-versions'.format(workspace_id))
        data = config_version_data()
        record = tfe_handler.TFERequest(api_endpoint, data, conf)
        log.info('Sending create configuraiton request.')
        return response_handler(record)
    else:
        log.error('Workspace id not provided.')


def get_upload_url(region, workspace_id):
    """Return the TFE workspace configuraiton version upload url."""
    response = create_config_version(region, workspace_id)
    upload_url = glom(response, 'data.attributes.upload-url', default=False)
    log.debug('found upload url: {}'.format(upload_url))
    return upload_url


def config_version_data():
    """TFE Confugration Version data."""
    return {
              "data": {
                "type": "configuration-versions",
                "attributes": {
                  "auto-queue-runs": True
                }
              }
            }


def upload_configuration_files(upload_url, tar_path):
    """Upload the configuration files to the target workspace."""
    log.info('uploading configuraiton file: {} to {}'.format(tar_path,
                                                             upload_url))
    if upload_url:
        headers = {'Content-Type': 'application/octet-stream'}
        with open(tar_path, 'rb') as f:
            b64 = base64.urlsafe_b64encode(f.read())
            req = urllib.request.Request(upload_url, b64, headers,
                                         method='PUT')
            response = urllib.request.urlopen(req)
            response = response.read()
            response = response.decode("utf-8")
            # Response is expected to be null
            log.info('Recieved response: {}'.format(response))
            return response
    else:
        log.error('Upload url not provided.')


def response_handler(record):
    """Evaulate response."""
    try:
        response = record.make_request()
        log.debug('Recieved response: {}'.format(response))
        return response
    except urllib.error.HTTPError as e:
        if e.code == 422:
            return "ERROR: Worspace already exists"
        else:
            return "ERROR"
