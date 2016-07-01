#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Brute strategy.

Schedule everything whenver it is available.
"""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import operator

from requests.exceptions import RequestException

from meister.schedulers.afl_scheduler import AFLScheduler

LOG = meister.strategies.LOG.getChild('priority')


class Priority(meister.strategies.BaseStrategy):
    """Priority strategy.

    Always have the highest priority jobs running, kill what we need to run.
    """

    def __init__(self, *args, **kwargs):
        """Create a priority strategy object."""
        super(self.__class__, self).__init__(*args, **kwargs)

    def run(self):
        """Run jobs based on priority."""
        # Sorting is not necessarily stable, and only by priority, we have other requirements too.
        jobs_to_schedule = sorted(self.jobs, key=operator.attrgetter('priority'), reverse=True)
        jobs_to_run = []

        # GJA = Greedy Job Allocator
        total_capacities = self._kube_total_capacity

        # TODO: We need to remove overhead, like database and meister, from total capacities.

        def _can_schedule(job):
            cpu_available = total_capacities['cpu'] >= job.limit_cpu
            memory_available = total_capacities['memory'] >= (job.limit_memory * 1024 ** 3)
            pod_available = total_capacities['pods'] >= 1
            return cpu_available and memory_available and pod_available

        def _schedule(job):
            LOG.debug("Scheduling new %s job with priority %d", job.worker, job.priority)
            total_capacities['cpu'] -= job.limit_cpu
            total_capacities['memory'] -= (job.limit_memory * 1024 ** 3)
            total_capacities['pods'] -= 1

            # We need to get the original JOB_ID in case the job is updated, hence saving it.
            job.save()
            jobs_to_run.append(job)

        while jobs_to_schedule and _can_schedule(jobs_to_schedule[0]):
            _schedule(jobs_to_schedule.pop(0))

        # TODO: We might still have some jobs that have the same priority but different requirements
        # and which are sorted differently, we need to solve the resource requirement equations for
        # the lowest priority we want to schedule, so that we maximize the use of our resources.

        # Collect all current jobs
        job_ids, worker_type = {}, {}
        for pod in pykube.objects.Pod.objects(self.api):
            if pod.ready:
                if 'job_id' in pod.obj['metadata']['labels']:
                    pod_name = pod.obj['metadata']['name']
                    job_ids[pod_name] = pod.obj['metadata']['labels']['job_id']
                    worker_type[pod_name] = pod.obj['metadata']['labels']['worker']
            else:
                LOG.warning("Encountered a Pod that is not ready: %s", pod)

        job_ids_to_run = set(job.id for job in jobs_scheduled)
        workers_to_kill = {k: v for k, v in job_ids.items() if v not in job_ids_to_run}
        job_ids_to_ignore = {v for v in job_ids.values() if v in job_ids_to_run}

        # Kill workers
        for worker, job_id in workers_to_kill.items():
            self.terminate(worker, worker_type[worker])     # TODO: refactor out the worker type
            LOG.debug("Killing worker for job %d", job_id)

        # Schedule jobs
        for job in jobs_to_run:
            if job.id in job_ids_to_ignore:
                LOG.debug("Starting new worker for job %d", job.id)
                self.schedule(jobs)
            else:
                LOG.debug("Worker already taking care of job %d", job.id)
