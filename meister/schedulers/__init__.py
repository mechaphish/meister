#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module containing the BaseStrategy."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import datetime
import itertools
import os
import time
import operator

# pylint: disable=import-error
import pykube.http
import pykube.objects
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
        self._node_capacities = None
        self._available_resources = None
        self._resources_cache_timeout = datetime.timedelta(seconds=30)
        self._resources_timestamp = datetime.datetime(1970, 1, 1, 0, 0, 0)

    def schedule(self, job):
        """Schedule the job with the specific resources."""
        job.save()
        if self._resources_available(job):
            self._resources_update(job)
            if job.worker == 'afl':
                self._schedule_kube_controller(job)
            else:
                self._schedule_kube_pod(job)
        return job

    @property
    def api(self):
        """Return the API we are working on."""
        if self._api is None:
            self._api = pykube.http.HTTPClient(kubernetes.from_env())
        return self._api

    def _kube_pod_template(self, job, restart_policy='Always'):
        name = "worker-{}".format(job.id)
        # FIXME
        cpu = str(job.limit_cpu) if job.limit_cpu is not None else 2
        memory = str(job.limit_memory) if job.limit_memory is not None else 4
        if os.environ.get('POSTGRES_USE_SLAVES') is not None:
            postgres_use_slaves = {'name': "POSTGRES_USE_SLAVES", 'value': "true"}
        else:
            postgres_use_slaves = None
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
                        'imagePullPolicy': os.environ['WORKER_IMAGE_PULL_POLICY'],
                        'resources': {
                            'limits': {
                                'cpu': str(cpu),
                                'memory': "{}Gi".format(memory)
                            }
                        },
                        'env': filter(None, [
                            {'name': "JOB_ID", 'value': str(job.id)},
                            postgres_use_slaves,
                            {'name': "POSTGRES_DATABASE_USER",
                             'value': os.environ['POSTGRES_DATABASE_USER']},
                            {'name': "POSTGRES_DATABASE_PASSWORD",
                             'value': os.environ['POSTGRES_DATABASE_PASSWORD']},
                            {'name': "POSTGRES_DATABASE_NAME",
                             'value': os.environ['POSTGRES_DATABASE_NAME']},
                        ])
                    }
                ]
            }
        }
        return config

    def _resources_available(self, job):
        """Internal method to check whether the resources for a Job are available."""
        assert job is not None
        cpu_available = self._kube_resources['cpu'] >= job.limit_cpu
        memory_available = self._kube_resources['memory'] >= (job.limit_memory * 1024 ** 3)
        pod_available = self._kube_resources['pods'] >= 1
        return cpu_available and memory_available and pod_available

    def _resources_update(self, job):
        """Internal method to check whether the resources for a Job are available."""
        assert job is not None
        self._kube_resources['cpu'] -= job.limit_cpu
        self._kube_resources['memory'] -= (job.limit_memory * 1024 ** 3)
        self._kube_resources['pods'] -= 1

    # Currently, we are using aggregate resources instead of per node resources for ease of
    # scheduling. This is suboptimal because we might run into situation where we think we can
    # schedule a job but actually cannot. The example below is a generalization of this in case node
    # specific information is retained.
    #
    # There is a possibly problem that we might have to use almost the latest information because
    # the following might happen:
    #  - node a has availability 2 cores / 1GB
    #  - node b has availability 2 cores / 2GB
    #  - we schedule 2 cores / 1GB, update our dict to substract from a
    #  - Kubernetes schedules it to run on node b
    #  - we want to schedule 2 cores / 2GB, our dict thinks we can on b
    #  - Kubernetes fails to spawn the worker
    @property
    def _kube_resources(self):
        """Internal helper method to collect resource data for Kubernetes cluster."""
        assert isinstance(self.api, pykube.http.HTTPClient)

        # meister running locally
        if 'KUBERNETES_SERVICE_HOST' not in os.environ or os.environ['KUBERNETES_SERVICE_HOST'] == "":
            self._available_resources = {'cpu': 99999, 'memory': 99999999999999, 'pods': 99999}
            return self._available_resources

        # Return cached data
        if (datetime.datetime.now() - self._resources_timestamp) <= self._resources_cache_timeout:
            return self._available_resources

        # Update node capacities, only ran once for the first update of availabe resources
        if self._node_capacities is None:
            nodes = pykube.objects.Node.objects(self.api).all()
            self._node_capacities = {}
            for node in nodes:
                cpu = _cpu2float(node.obj['status']['capacity']['cpu'])
                memory = _memory2int(node.obj['status']['capacity']['memory'])
                pods = int(node.obj['status']['capacity']['pods'])
                self._node_capacities[node.name] = {'cpu': cpu,
                                                    'memory': memory,
                                                    'pods': pods}

        # Reset available resources
        self._available_resources = {'cpu': 0.0, 'memory': 0L, 'pods': 0}
        for capacity in self._node_capacities.values():
            self._available_resources['cpu'] += capacity['cpu']
            self._available_resources['memory'] += capacity['memory']
            self._available_resources['pods'] += capacity['pods']

        # Collect fresh information from the Kubernetes API about all running pods
        # FIXME: Shitty loop to fix https://github.com/kelproject/pykube/issues/10
        pods = []
        for pod in pykube.objects.Pod.objects(self.api):
            try:
                if pod.ready: pods.append(pod)
            except KeyError:
                pass
        for pod in pods:
            # FIXME: We are assuming that each pod only has one container here
            try:
                resources = pod.obj['spec']['containers'][0]['resources']['limits']
            except KeyError:
                resources = pod.obj['spec']['containers'][0]['resources']['requests']
            self._available_resources['cpu'] -= _cpu2float(resources['cpu'])
            self._available_resources['memory'] -= _memory2int(resources['memory'])
            self._available_resources['pods'] -= 1
        self._resources_timestamp = datetime.datetime.now()

        return self._available_resources

    def _schedule_kube_controller(self, job):
        """Internal method to schedule a never ending job on Kubernetes."""
        assert isinstance(self.api, pykube.http.HTTPClient)
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
                pykube.objects.ReplicationController(self.api, config).create()
        except HTTPError as error:
            if error.response.status_code == 409:
                LOG.warning("Job already scheduled %s", job.id)
            else:
                raise error

    def _schedule_kube_pod(self, job):
        """Internal method to schedule a job on Kubernetes."""
        assert isinstance(self.api, pykube.http.HTTPClient)
        config = self._kube_pod_template(job, 'Never')

        try:
            if 'KUBERNETES_SERVICE_HOST' in os.environ:
                pykube.objects.Pod(self.api, config).create()
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
