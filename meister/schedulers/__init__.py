#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module containing the BaseStrategy."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import itertools
import os
import time

# pylint: disable=import-error
from pykube.http import HTTPClient
from pykube.objects import ReplicationController, Pod, Node
# pylint: disable=import-error
from requests.exceptions import HTTPError

import meister.log
import meister.kubernetes as kubernetes

from farnsworth.models.challenge_binary_node import ChallengeBinaryNode

LOG = meister.log.LOG.getChild('schedulers')


def _cpu2float(cpu):
    """Internal helper function to convert Kubernetes CPU numbers to float."""
    if cpu.endswith("m"):
        cpu = int(cpu[:-1]) / 1000.
    else:
        return float(cpu)


def _memory2int(memory):
    """Internal helper function to convert Kubernetes memory amount to integers."""
    multiplier = 1
    if memory.endswith("Ki"):
        multiplier = 1024
    elif memory.endswith("Mi"):
        multiplier = 1024 ** 2
    elif memory.endswith("Gi"):
        multiplier = 1024 ** 3
    return int(memory[:-2]) * multiplier


class KubernetesScheduler(object):
    """Kubernetes scheduler class, should be inherited by actual schedulers."""

    def __init__(self):
        """Create base scheduler.

        Create the base scheduler, you should call this from your scheduler to
        make sure that all class variables are set up properly.
        """
        self._api = None

    def schedule(self, job):
        """Schedule the job with the specific resources."""
        job.save()
        if self._resources_available(job):
            if job.worker == 'afl':
                self._schedule_kube_controller(job)
            else:
                self._schedule_kube_pod(job)
        return job

    @property
    def api(self):
        """Return the API we are working on."""
        if self._api is None:
            self._api = HTTPClient(kubernetes.from_env())
        return self._api

    def _kube_pod_template(self, job, restart_policy='Always'):
        name = "worker-{}".format(job.id)
        # FIXME
        cpu = str(job.limit_cpu) if job.limit_cpu is not None else 2
        memory = str(job.limit_memory) if job.limit_memory is not None else 4
        config = {
            'metadata': {
                'labels': {
                    'app': 'worker',
                    'worker': job.worker,
                    'job_id': str(job.id),
                },
                'name': name
            },
            'spec': {
                'restartPolicy': restart_policy,
                'containers': [
                    {
                        'name': name,
                        'image': os.environ['WORKER_IMAGE'],
                        'resources': {
                            'requests': {
                                'cpu': str(cpu),
                                'memory': "{}Gi".format(memory)
                            }
                        },
                        'env': [
                            {'name': "JOB_ID", 'value': str(job.id)},
                            {'name': "POSTGRES_USE_SLAVES", 'value': "true"},
                            {'name': "POSTGRES_DATABASE_USER",
                             'value': os.environ['POSTGRES_DATABASE_USER']},
                            {'name': "POSTGRES_DATABASE_PASSWORD",
                             'value': os.environ['POSTGRES_DATABASE_PASSWORD']},
                            {'name': "POSTGRES_DATABASE_NAME",
                             'value': os.environ['POSTGRES_DATABASE_NAME']},
                        ]
                    }
                ]
            }
        }
        return config

    def _resources_available(self, job):
        """Internal method to check whether the resources for a Job are available."""
        # TODO: Check if resources are available for the job
        assert job is not None
        self._kube_aggregate_resources()
        return True

    # TODO: We want to cache the results in a worst-case sense for some time
    # TODO: Use as property instead, so that callers can update it if necessary
    def _kube_aggregate_resources(self):
        """Internal helper method to collect aggregate statistics for Kubernetes cluster."""
        assert isinstance(self.api, HTTPClient)
        nodes = Node.objects(self.api)
        assert nodes is not None
        # TODO: collect available resources per node
        # TODO: set instance directory to available resources

    def _schedule_kube_controller(self, job):
        """Internal method to schedule a never ending job on Kubernetes."""
        assert isinstance(self.api, HTTPClient)
        name = "worker-{}".format(job.id)
        config = {
            'metadata': {'name': name},
            'spec': {
                'replicas': 1,
                'selector': {'job_id': str(job.id)},
                'template': self._kube_pod_template(job)
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

    def _schedule_kube_pod(self, job):
        """Internal method to schedule a job on Kubernetes."""
        assert isinstance(self.api, HTTPClient)
        config = self._kube_pod_template(job, 'Never')

        try:
            if 'KUBERNETES_SERVICE_HOST' in os.environ:
                Pod(self.api, config).create()
        except HTTPError as error:
            if error.response.status_code == 409:
                LOG.warning("Job already scheduled %s", job.id)
            else:
                raise error


class BaseScheduler(KubernetesScheduler):
    """Base strategy.

    All other scheduling strategies should inherit from this Strategy.
    """

    def __init__(self, **kwargs):
        """Construct a base strategy object.

        The Base Strategy assumes that the Farnsworth API is setup already,
        and uses it directly.

        :argument cgc: a CGCAPI object, so that we can talk to the CGC API.
        :keyword sleepytime: the amount to sleep between strategy runs.
        """
        cgc = kwargs.pop('cgc')
        sleepytime = kwargs.pop('sleepytime', 3)
        creators = kwargs.pop('creators', [])
        super(BaseScheduler, self).__init__(**kwargs)

        self.cgc = cgc
        self.sleepytime = sleepytime
        LOG.debug("Scheduler sleepytime: %d", self.sleepytime)
        self.creators = creators if creators is not None else []
        LOG.debug("Job creators: %s", ", ".join(c.__class__.__name__
                                                for c in self.creators))

    def sleep(self):
        """Sleep a pre-defined interval."""
        LOG.debug("Sleepytime...")
        time.sleep(self.sleepytime)

    @property
    def round(self):
        """Return the number of the active round."""
        return self.cgc.getRound()

    @property
    def jobs(self):
        """Return all jobs that all creators want to run."""
        return itertools.chain.from_iterable(c.jobs for c in self.creators)
