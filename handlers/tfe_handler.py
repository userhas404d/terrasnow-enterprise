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

    def __init__(self, target, data, conf):
        """Consturct TFE REST call."""
        self.host = conf.get("TERRAFORM_ENTERPRISE", "INSTANCE_NAME")
        self.atlas_token = conf.get("TERRAFORM_ENTERPRISE", "ATLAS_TOKEN")
        self.target = target
        self.headers = {'Authorization': 'Bearer {}'.format(self.atlas_token)}
        self.base_url = 'https://{}/api/v2'.format(self.host)
        self.data = self.parse_data(data)
        self.url = self.base_url + self.target
        self.response = None

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
        # urllib sends a GET request by default, unless data is included
        if self.data:
            log.info('Making POST request against url: {}'.format(self.url))
            self.headers['Content-Type'] = "application/vnd.api+json"
            req = urllib.request.Request(self.url, self.data, self.headers)
            self.response = urllib.request.urlopen(req)
            return self.eval_response()
        else:
            log.info('Making GET request against url: {}'.format(self.url))
            req = urllib.request.Request(self.url, self.data, self.headers)
            self.response = urllib.request.urlopen(req)
            return self.eval_response()

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
    record = TFERequest('/organizations/plus3it-poc/oauth-tokens', None, conf)
    response = record.make_request()
    return glom(response, 'data.0.id', default=False)


# modules


def get_add_module_data(repo_namespace):
    """Return add moudule data block."""
    return {
            "data": {
                "attributes":
                {
                 "vcs-repo": {
                   "identifier": "{}".format(repo_namespace),
                   "oauth-token-id": "{}".format(get_vcs_oauth())
                  }
                },
                "type": "registry-modules"
              }
            }


def add_module(repo_namespace, conf):
    """Add module to terrafrom enterprise private module registry."""
    record = TFERequest('/registry-modules',
                        get_add_module_data(repo_namespace), conf)
    response = record.make_request()
    return response
