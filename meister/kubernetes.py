#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Manage Kubernetes configurations."""

import os
import pykube.config


def config_from_env():
    """Get a Kubernetes configuration from environment variables."""
    if 'KUBERNETES_SERVICE_USE_SSL' in os.environ:
        protocol = 'https'
    else:
        protocol = 'http'
    host = os.environ.get('KUBERNETES_SERVICE_HOST', 'localhost')
    port = os.environ.get('KUBERNETES_SERVICE_PORT', 8080)
    user = os.environ.get('KUBERNETES_SERVICE_USER', 'admin')
    token = os.environ.get('KUBERNETES_SERVICE_TOKEN', '')

    config = {
        'apiVersion': 'v1',
        'clusters': [
            {'cluster':
             {'insecure-skip-tls-verify': True,
              'server': "{}://{}:{}".format(protocol, host, port)},
             'name': 'ubuntu'}
        ],
        'contexts': [
            {'context':
             {'cluster': 'ubuntu',
              'user': user},
             'name': 'ubuntu'}
        ],
        'current-context': 'ubuntu',
        'kind': 'Config',
        'preferences': {},
        'users': [
            {'name': user,
             'user':
             {'token': token}}
        ]
    }

    return pykube.config.KubeConfig(config)
