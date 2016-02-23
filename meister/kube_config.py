from os import environ as ENV
from pykube.config import KubeConfig

kubemaster_url = "{}://{}:{}".format(
    'https' if ENV['KUBERNETES_SERVICE_USE_SSL'] == 'True' else 'http',
    ENV['KUBERNETES_SERVICE_HOST'],
    ENV['KUBERNETES_SERVICE_PORT']
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
          'user': ENV['KUBERNETES_SERVICE_USER']},
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
