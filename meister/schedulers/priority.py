#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Priority Scheduler.

Schedule everything whenver it is available.
"""

from __future__ import unicode_literals, absolute_import

import copy
import operator

import concurrent.futures
import farnsworth.config
from farnsworth.models.job import TesterJob
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

    def _run(self):
        """Run jobs based on priority."""
        # Sorting is not necessarily stable, and only by priority, we have other requirements too.

        # GJA = Greedy Job Allocator
        total_capacities = copy.deepcopy(self._kube_total_capacity)

        # TODO: We need to remove overhead, like database and meister, from total capacities.

        def _can_schedule(job):
            cpu_available = total_capacities['cpu'] >= job.request_cpu
            memory_available = total_capacities['memory'] >= (job.request_memory * 1024 ** 2)
            pod_available = total_capacities['pods'] >= 1
            return cpu_available and memory_available and pod_available

        def _account_for_resources(job):
            LOG.debug("Scheduling new %s job with priority %d", job.worker, job.priority)
            total_capacities['cpu'] -= job.request_cpu
            total_capacities['memory'] -= (job.request_memory * 1024 ** 2)
            total_capacities['pods'] -= 1

        jobs_to_run, job_ids_to_run = [], set()
        with farnsworth.config.master_db.atomic():
            for j, p in self.brain.sort(self.jobs):
                if not _can_schedule(j):
                    LOG.debug("Resources exhausted, stopping scheduling")
                    break

                # FIXME: We always want to create new TesterJob to spawn
                # up a VM if none is running. In the worst case, we
                # spawn up an extra one and speed up processing.  In the
                # very worst case, we have ONLY testing jobs.
                kwargs = {df.name: getattr(j, df.name) for df in j.dirty_fields}

                job, created = type(j).get_or_create(**kwargs)
                if isinstance(j, TesterJob):
                    job.completed_at = None

                if job.completed_at is not None:
                    LOG.debug("Job has been completed at %s, skipping", job.completed_at)
                    continue

                if created:
                    LOG.debug("Job did not exist yet, created it")

                if job.id not in job_ids_to_run:
                    LOG.debug("Scheduling job id=%d type=%s", job.id, job.worker)
                    _account_for_resources(job)
                    if job.priority != p:
                        job.priority = p
                        job.save()
                    jobs_to_run.append(job)
                    job_ids_to_run.add(job.id)
                else:
                    LOG.error("A creator yielded a job a second time: job id=%d", job.id)

        # TODO: We might still have some jobs that have the same priority but different requirements
        # and which are sorted differently, we need to solve the resource requirement equations for
        # the lowest priority we want to schedule, so that we maximize the use of our resources.

        job_ids_to_run = set(job.id for job in jobs_to_run)
        LOG.debug("Jobs to run: %s", job_ids_to_run)

        if job_ids_to_run:
            assert isinstance(list(job_ids_to_run)[0], (int, long))

        # Collect all current jobs
        job_ids_to_kill, job_ids_to_ignore = [], []
        pending_pods = pykube.objects.Pod.objects(self.api).filter(field_selector={"status.phase": "Pending"})
        running_pods = pykube.objects.Pod.objects(self.api).filter(field_selector={"status.phase": "Running"})

        # Delay in API calls may result in change of number of pending/running pods
        pods = [p for p in pending_pods] + [p for p in running_pods]
        for pod in pods:
            if 'job_id' in pod.obj['metadata']['labels']:
                job_id = int(pod.obj['metadata']['labels']['job_id'])
                if job_id in job_ids_to_run:
                    job_ids_to_ignore.append(job_id)
                else:
                    # We do not kill jobs that have been completed to keep the logs around. We do
                    # want to kill jobs that are still in the processing stage though.
                    # See states docs http://kubernetes.io/docs/user-guide/pod-states/
                    if pod.running or pod.pending:
                        job_ids_to_kill.append(job_id)
                    else:
                        LOG.warning("Encountered a Pod that is not ready (running or completed): %s",
                                    pod.obj['metadata']['name'])

        if job_ids_to_kill:
            assert isinstance(job_ids_to_kill[0], (int, long))

        if job_ids_to_ignore:
            assert isinstance(job_ids_to_ignore[0], (int, long))

        LOG.debug("Terminating workers: %s", job_ids_to_kill)
        LOG.debug("Workers running already: %s", job_ids_to_ignore)

        # Kill workers
        def _terminate(job_id):
            LOG.debug("Killing worker for job %s", job_id)
            self.terminate(self._worker_name(job_id))

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(_terminate, job_ids_to_kill)

        # Schedule jobs
        def _schedule(job):
            if job.id not in job_ids_to_ignore:
                LOG.debug("Scheduling %s for cs=%s cbn=%s", job.__class__.__name__, job.cs_id,
                          job.cbn_id)
                self.schedule(job)
            else:
                LOG.debug("Worker already taking care of job %d", job.id)

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(_schedule, jobs_to_run)

        self._kube_resources
