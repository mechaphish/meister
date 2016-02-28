#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Job scheduler."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

from pykube.http import HTTPClient
from pykube.objects import ReplicationController
from requests.exceptions import HTTPError
from os import environ as ENV

import meister.kubernetes as kubernetes
from farnsworth_client.models import Job


class Scheduler(object):

    """Abstract scheduler class, should be inherited by actual schedulers."""

    def __init__(self):
        """Create base scheduler.

        Create the base scheduler, you should call this from your scheduler to
        make sure that all class variables are set up properly.
        """
        self._api = None

    def schedule(self, worker, cbn, cpus, memory):
        """Schedule the job with the specific resources."""
        job = Job.find_by(worker=worker, cbn_id=cbn.id)
        if job is None:
            # We have to explicitly compare to None, job might evaluate to False
            job = Job.create(worker=worker, cbn_id=cbn.id, limit_cpu=cpus,
                             limit_memory=memory, payload=cbn)
        self._schedule_kube_controller(job, cpus, memory)
        return job

    @property
    def api(self):
        """Return the API we are working on."""
        if self._api is None:
            self._api = HTTPClient(kubernetes.config_from_env())
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
            if ENV['KUBERNETES_SERVICE_HOST']:
                ReplicationController(self.api, config).create()
        except HTTPError as error:
            if error.response.status_code == 409:
                # FIXME: use log instead of print
                print("Already scheduled")
            else:
                raise error
