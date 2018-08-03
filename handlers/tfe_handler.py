"""Get Terraform Enterprise data via REST."""

import json
import logging as log
import urllib.parse
import urllib.request

from glom import glom

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(level=log.DEBUG, format=FORMAT)


class TFERequest(object):
    """Terraform Enterprise record."""

    def __init__(self, target, data, conf, file=None):
        """Consturct TFE REST call."""
        self.host = conf.get("TERRAFORM_ENTERPRISE", "INSTANCE_NAME")
        self.atlas_token = conf.get("TERRAFORM_ENTERPRISE", "ATLAS_TOKEN")
        self.target = target
        self.headers = {'Authorization': 'Bearer {}'.format(self.atlas_token)}
        self.base_url = 'https://{}/api/v2'.format(self.host)
        self.data = self.parse_data(data)
        self.url = self.base_url + self.target
        self.response = None
        self.file = file

    def parse_data(self, data):
        """Parse data."""
        if data:
            if type(data) is dict:
                return json.dumps(data).encode("utf-8")
            else:
                return urllib.parse.urlencode(data).encode("utf-8")
        else:
            return None

    def make_request(self):
        """Make request."""
        if self.file:
            print("RECIEVED FILE REQUEST.")
        elif self.data:
            log.info('Making POST request against url: {}'.format(self.url))
            self.headers['Content-Type'] = "application/vnd.api+json"
            req = urllib.request.Request(self.url, self.data, self.headers)
            log.debug('url request: {}'.format(self.url))
            log.debug('request data: {}'.format(self.data))
            log.debug('request headers: {}'.format(self.headers))
            self.response = urllib.request.urlopen(req)
            response = self.eval_response()
            log.debug("recieved response: {}".format(response))
            return response
        else:
            log.info('Making GET request against url: {}'.format(self.url))
            req = urllib.request.Request(self.url, self.data, self.headers)
            self.response = urllib.request.urlopen(req)
            response = self.eval_response()
            log.debug("recieved response: {}".format(response))
            return response

    def delete(self):
        """Make delete request."""
        log.info('Making DELETE request against url: {}'.format(self.url))
        req = urllib.request.Request(self.url, self.data, self.headers,
                                     method='DELETE')
        self.response = urllib.request.urlopen(req)
        return self.eval_response()

    def eval_response(self):
        """Convert response to dict."""
        log.info('Returning response for standard request.')
        self.response = self.response.read()
        self.response = self.response.decode("utf-8")
        return json.loads(self.response)


def get_vcs_oauth(conf):
    """Return VCS Oauth token."""
    org = conf.get("TERRAFORM_ENTERPRISE", "ORGANIZATION")
    record = TFERequest('/organizations/{}/oauth-tokens'.format(org), None,
                        conf)
    response = record.make_request()
    response = glom(response, 'data.0.id', default=False)
    if response:
        return response
    else:
        log.error(
          'VCS oauth id not found in reponse from TFE instance. Confirm' +
          'that a VCS has been configured for the TFE organization.')
        return False
