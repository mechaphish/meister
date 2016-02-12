import requests
from requests.auth import HTTPDigestAuth
import json
import glob
import base64
import ntpath
import os
from urlparse import urljoin
from .errors import *

class API:
    def __init__(self, base_url, user, password):
        self.base_url = base_url
        self.user = user
        self.password = password

    def _url(self, path):
        return urljoin(self.base_url, path)

    def _get(self, path):
        resp = requests.get(
            self._url(path),
            auth=HTTPDigestAuth(self.user, self.password)
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            raise APIError('Error {} on GET {}'.format(resp.status_code, path))

    def status(self):
        return self._get('/status')

    def binaries(self, round_n):
        binaries_path = os.getenv(
            'CB_PATH_FIXME',
            '/home/nebirhos/Work/SecLab/CyberGrandChallenge/cbs/'
        )
        binaries = glob.glob(binaries_path + 'qualifier_event/*/*')
        bin_data = []
        for binary in binaries:
            b = open(binary, 'rb')
            b64_bin = base64.b64encode(b.read())
            bin_data.append({
                'cbid': ntpath.basename(binary),
                'data': b64_bin
            })
        return {
            'binaries': bin_data
        }
