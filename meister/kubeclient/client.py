import requests
import json
from urlparse import urljoin

class Client():
    def __init__(self, base_uri, version='v1'):
        self.base_uri = base_uri
        self.version = version

    def _url(self, *paths):
        resource = '/'.join(('api', self.version) + paths)
        return urljoin(self.base_uri, resource)

    def _get(self, resource):
        resp = requests.get(resource)
        if resp.status_code == 200:
            return resp.json()

    def _post(self, resource, data):
        resp = requests.post(resource, data)
        if resp.status_code == 200:
            return resp.json()

    def replications(self, namespace='default'):
        resource = self._url('namespaces', namespace, 'replicationcontrollers')
        return self._get(resource)

    def createReplication(self,
                          name,
                          image,
                          replicas,
                          namespace='default'):
        resource = self._url('namespaces', namespace, 'replicationcontrollers')
        data = {
            'metadata': {'name': name},
            'spec': {
                'replicas': replicas,
                'selector': {'app': name},
                'template': {
                    'metadata': {
                        'name': name,
                        'labels': {'app': name}
                    },
                    'spec': {
                        'containers': [{
                            'name': name,
                            'image': image
                        }]
                    }
                }
            }
        }
        return self._post(resource, data)
