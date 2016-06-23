#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Manage Kubernetes configurations."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import os

# pylint: disable=import-error
import pykube.config
# pylint: enable=import-error


def from_env():
    """Get a Kubernetes configuration from environment variables."""
    if 'KUBERNETES_SERVICE_USE_SSL' in os.environ:
        protocol = 'https'
    else:
        protocol = 'http'
    host = os.environ.get('KUBERNETES_SERVICE_HOST', 'localhost')
    port = os.environ.get('KUBERNETES_SERVICE_PORT', 8080)
    user = os.environ.get('KUBERNETES_SERVICE_USER', 'admin')
    token = os.environ.get('KUBERNETES_SERVICE_TOKEN', 'xxx')

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
