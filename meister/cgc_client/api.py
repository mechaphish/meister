#!/usr/bin/env python3
# -* coding: utf-8 -*-

"""API client to talk to the CGC API."""

import glob
import base64
import os
import os.path

from urllib.parse import urljoin

import requests
from requests.auth import HTTPDigestAuth

from .errors import CGCAPIError


def from_env():
    """Create a CGC API Object from environment variables."""
    url = os.environ.get('CGC_API_URL', 'localhost')
    user = os.environ.get('CGC_API_USER', 'shellphish')
    password = os.environ.get('CGC_API_PASS', 'shellphish')
    binaries_path = os.environ.get('CGC_CB_PATH', '/tmp/')

    return CGCAPI(url, user, password, binaries_path)


class CGCAPI(object):

    """Wrapper to talk to the CGC API."""

    def __init__(self, url, user, password, binaries_path):
        """Create the CGC API wrapper."""
        self.url = url
        self.user = user
        self.password = password
        self.binaries_path = binaries_path

    def _url(self, path):
        return urljoin(self.url, path)

    def _get(self, path):
        resp = requests.get(self._url(path),
                            auth=HTTPDigestAuth(self.user, self.password))
        if resp.status_code == 200:
            return resp.json()
        else:
            reason = "Error {} on GET {}".format(resp.status_code, path)
            raise CGCAPIError(reason)

    def status(self):
        """Retrieve the current status."""
        return self._get('/status')

    def binaries(self, round_n):
        """Return all available binaries."""
        # NOTE: Why is this happening on disk instead of at the API?
        binaries_files = glob.glob(os.path.join(self.binaries_path,
                                                'qualifier_event/*/*'))
        binaries = []
        for binary in binaries_files:
            with open(binary) as b:
                bin_data.append({'cbid': os.path.basename(binary),
                                 'data': base64.b64encode(b.read())})
        return {'binaries': binaries}
