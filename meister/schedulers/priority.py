#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Priority Scheduler.

Schedule everything whenver it is available.
"""

from __future__ import unicode_literals, absolute_import

import operator

import pykube.objects

import meister.schedulers

LOG = meister.schedulers.LOG.getChild('priority')


class PriorityScheduler(meister.schedulers.BaseScheduler):
    """Priority scheduler.

    Always have the highest priority jobs running, kill what we need to run.
    """

    def __init__(self, *args, **kwargs):
        """Create a priority strategy object."""
        super(PriorityScheduler, self).__init__(*args, **kwargs)
        LOG.debug("PriorityScheduler time!")

    def run(self):
        """Run jobs based on priority."""
        if self._is_kubernetes_unavailable():
            return self.dry_run()

        # Sorting is not necessarily stable, and only by priority, we have other requirements too.
        jobs_to_schedule = sorted((j for j in self.jobs if j.completed_at is None),
                                  key=operator.attrgetter('priority'), reverse=True)
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

        if jobs_to_schedule:
            LOG.debug("Can I schedule the highest priority job? %s",
                    _can_schedule(jobs_to_schedule[0]))
        else:
            LOG.debug("No jobs to schedule, tabula rasa!")

        while jobs_to_schedule and _can_schedule(jobs_to_schedule[0]):
            _schedule(jobs_to_schedule.pop(0))

        # TODO: We might still have some jobs that have the same priority but different requirements
        # and which are sorted differently, we need to solve the resource requirement equations for
        # the lowest priority we want to schedule, so that we maximize the use of our resources.

        # Collect all current jobs
        job_ids = {}
        for pod in pykube.objects.Pod.objects(self.api):
            if pod.ready:
                if 'job_id' in pod.obj['metadata']['labels']:
                    pod_name = pod.obj['metadata']['name']
                    job_ids[pod_name] = pod.obj['metadata']['labels']['job_id']
            else:
                LOG.warning("Encountered a Pod that is not ready: %s", pod.obj['metadata']['name'])

        LOG.debug("Jobs not running: %s", set(job.id for job in jobs_to_schedule))

        job_ids_to_run = set(str(job.id) for job in jobs_to_run)
        LOG.debug("Jobs to run: %s", job_ids_to_run)

        workers_to_kill = {k: v for k, v in job_ids.items() if str(v) not in job_ids_to_run}
        LOG.debug("Killing: %s", workers_to_kill)

        job_ids_to_ignore = {v for v in job_ids.values() if str(v) in job_ids_to_run}
        LOG.debug("Not touching: %s", job_ids_to_ignore)

        # Kill workers
        for worker, job_id in workers_to_kill.items():
            LOG.debug("Killing worker for job %s", job_id)
            self.terminate(worker)     # TODO: refactor out the worker type

        # Schedule jobs
        for job in jobs_to_run:
            if job.id not in job_ids_to_ignore:
                LOG.debug("Scheduling %s for %s", job.__class__.__name__,
                          job.cbn_id)
                self.schedule(job)
            else:
                LOG.debug("Worker already taking care of job %d", job.id)
