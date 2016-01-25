import requests
import json
from urlparse import urljoin

class Client():
    def __init__(self, base_uri, version='v1'):
        self.base_uri = base_uri
        self.version = version

    def _url(self, paths):
        resource = '/'.join(('api', self.version) + paths)
        return urljoin(self.base_uri, resource)

    def _get(self, *paths):
        resp = requests.get(self._url(paths))
        if resp.status_code == 200:
            return resp.json()

    def replications(self, namespace='default'):
        return self._get('namespaces', namespace, 'replicationcontrollers')

    def createReplication(self,
                          name,
                          image,
                          replicas,
                          namespace='default'):
        return self._post('namespaces', namespace,
                          'replicationcontrollers', data)
