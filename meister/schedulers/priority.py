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

        job_ids_to_run = set(job.id for job in jobs_to_run)
        LOG.debug("Jobs to run: %s", job_ids_to_run)

        assert isinstance(list(job_ids_to_run)[0], (int, long))

        # Collect all current jobs
        job_ids_to_kill, job_ids_to_ignore = [], []
        for pod in pykube.objects.Pod.objects(self.api):
            if pod.ready:
                if 'job_id' in pod.obj['metadata']['labels']:
                    job_id = int(pod.obj['metadata']['labels']['job_id'])
                    if job_id in job_ids_to_run:
                        job_ids_to_ignore.append(job_id)
                    else:
                        job_ids_to_kill.append(job_id)
            else:
                LOG.warning("Encountered a Pod that is not ready: %s", pod.obj['metadata']['name'])

        if job_ids_to_kill:
            assert isinstance(job_ids_to_kill[0], (int, long))

        if job_ids_to_ignore:
            assert isinstance(job_ids_to_ignore[0], (int, long))

        LOG.debug("Jobs not running: %s", set(job.id for job in jobs_to_schedule))
        LOG.debug("Terminating workers: %s", job_ids_to_kill)
        LOG.debug("Workers running already: %s", job_ids_to_ignore)

        # Kill workers
        for job_id in job_ids_to_kill:
            LOG.debug("Killing worker for job %s", job_id)
            self.terminate(self._worker_name(job_id))

        # Schedule jobs
        for job in jobs_to_run:
            if job.id not in job_ids_to_ignore:
                LOG.debug("Scheduling %s for %s", job.__class__.__name__,
                          job.cbn_id)
                self.schedule(job)
            else:
                LOG.debug("Worker already taking care of job %d", job.id)
