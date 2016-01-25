from os import getenv as ENV
from .kubeclient.client import Client

class Scheduler(object):
    def __init__(self):
        base_uri = "http://%s:8080/" % ENV('KUBERNETES_SERVICE_HOST')
        self.client = Client(base_uri)

    def schedule(self, name):
        return self.client.createReplication(name=name, image='foo', replicas=10)
