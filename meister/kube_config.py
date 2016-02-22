from os import environ as ENV
from pykube.config import KubeConfig

kubemaster_url = "http://{}:{}".format(
    ENV['KUBERNETES_SERVICE_HOST'], ENV['KUBERNETES_SERVICE_PORT']
)
config_data = {
    'apiVersion': 'v1',
    'clusters': [
        {'cluster':
         {'insecure-skip-tls-verify': True,
          'server': kubemaster_url},
         'name': 'ubuntu'}
    ],
    'contexts': [
        {'context':
         {'cluster': 'ubuntu',
          'user': 'admin'},
         'name': 'ubuntu'}
    ],
    'current-context': 'ubuntu',
    'kind': 'Config',
    'preferences': {},
    'users': [
        {'name': ENV['KUBERNETES_SERVICE_USER'],
         'user': {'token': ENV['KUBERNETES_SERVICE_TOKEN']}}
    ]
}

kube_config = KubeConfig(config_data)
