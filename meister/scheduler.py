#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Job scheduler."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import os

from pykube.http import HTTPClient
from pykube.objects import ReplicationController
from requests.exceptions import HTTPError

from meister.log import LOG
import meister.kubernetes as kubernetes
from farnsworth_client.models import Job

LOG = meister.log.getChild('scheduler')


class Scheduler(object):

    """Abstract scheduler class, should be inherited by actual schedulers."""

    def __init__(self):
        """Create base scheduler.

        Create the base scheduler, you should call this from your scheduler to
        make sure that all class variables are set up properly.
        """
        self._api = None

    def schedule(self, job):
        """Schedule the job with the specific resources."""
        job.save_if_not_existing()
        self.schedule_kube_controller(job, job.limit_cpu, job.limit_memory)
        return job

    @property
    def api(self):
        """Return the API we are working on."""
        if self._api is None:
            self._api = HTTPClient(kubernetes.from_env())
        return self._api

    def _schedule_kube_controller(self, job, cpus, memory):
        """Internal method to schedule a job on Kubernetes."""
        assert isinstance(self.api, HTTPClient)
        name = "worker-{}".format(job.id)
        config = {
            'metadata': {'name': name},
            'spec': {
                'replicas': 1,
                'selector': {'job_id': str(job.id)},
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'worker',
                            'worker': job.worker,
                            'job_id': str(job.id),
                        },
                        'name': name
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': name,
                                'image': 'worker',
                                'resources': {
                                    'requests': {
                                        'cpu': str(cpus),
                                        'memory': "{}Gi".format(memory)
                                    }
                                },
                                'env': [
                                    {'name': "JOB_ID", 'value': str(job.id)}
                                ]
                            }
                        ]
                    }
                }
            }
        }

        try:
            if 'KUBERNETES_SERVICE_HOST' in os.environ:
                ReplicationController(self.api, config).create()
        except HTTPError as error:
            if error.response.status_code == 409:
                LOG.warning("Job already scheduled %s", job.id)
            else:
                raise error
