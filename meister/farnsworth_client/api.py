import os
import requests
from urlparse import urljoin

class API:
    def __init__(self, base_url):
        self.base_url = base_url

    def _url(self, path):
        return urljoin(self.base_url, path)

    def add_cb(self, name, data):
        return requests.post(
            self._url("/cbs"),
            json = {"name": name, "data": data}
        )
