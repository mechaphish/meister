#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Priority Scheduler.

Schedule everything whenver it is available.
"""

from __future__ import unicode_literals, absolute_import

import copy
import operator
import os

import concurrent.futures
import farnsworth.config
from farnsworth.models.job import AFLJob, TesterJob, Job
import pykube.objects

import meister.schedulers

LOG = meister.schedulers.LOG.getChild('priority')


class PriorityScheduler(meister.schedulers.BaseScheduler):
    """Priority scheduler.

    Always have the highest priority jobs running, kill what we need to run.
    """

    def __init__(self, *args, **kwargs):
        """Create a priority strategy object."""
        self.staggering = int(os.environ['MEISTER_PRIORITY_STAGGERING'])
        self.stagger_factor = float(os.environ['MEISTER_PRIORITY_STAGGER_FACTOR'])
        super(PriorityScheduler, self).__init__(*args, **kwargs)
        LOG.debug("PriorityScheduler time!")

    def _run(self):
        """Run jobs based on priority."""
        # Our Greedy Job Allocator (GJA) is not optimal.
        # It does work well enough in our tests though. A problem is
        # that we might still have some jobs that have the same priority
        # but different requirements and which are sorted differently
        # each time (as in, not necessarily in a total order).
        # For now, we do not optimize for the highest number of jobs at
        # the lowest priority because the unused resources each
        # scheduling round will be very small in comparison to all
        # resources.
        # Note, however, that in the worst case, we will kill the lowest
        # priority jobs in an oscillatory fashion at each scheduling
        # round.
        total_capacities = copy.deepcopy(self._kube_total_capacity)

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

                # We need to set completed_at to None if the TesterJob
                # has finished because it will almost always exist for
                # this CS already and we would otherwise not test
                # anything for this CS and this worker type anymore.
                # If it hasn't completed yet, it will pick up the
                # individual jobs that we have already created at this
                # point in the brain
                kwargs = {df.name: getattr(j, df.name) for df in j.dirty_fields}
                job, created = type(j).get_or_create(**kwargs)

                if isinstance(j, (AFLJob, TesterJob)):
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
                        LOG.debug("Priority changed from %d to %d", job.priority, p)
                        job.priority = p
                        job.save()
                    jobs_to_run.append(job)
                    job_ids_to_run.add(job.id)
                else:
                    LOG.error("A creator yielded a job a second time: job id=%d", job.id)

        job_ids_to_run = set(job.id for job in jobs_to_run)
        LOG.debug("Jobs to run: %s", job_ids_to_run)

        if job_ids_to_run:
            assert isinstance(list(job_ids_to_run)[0], (int, long))

        # Collect all current jobs
        job_ids_to_kill, pods_to_kill, job_ids_to_ignore = [], [], set()
        pending_pods = pykube.objects.Pod.objects(self.api).filter(field_selector={"status.phase": "Pending"})
        running_pods = pykube.objects.Pod.objects(self.api).filter(field_selector={"status.phase": "Running"})

        # Delay in API calls may result in change of number of pending/running pods
        pods = [p for p in pending_pods] + [p for p in running_pods]
        for pod in pods:
            if 'job_id' in pod.obj['metadata']['labels']:
                job_id = int(pod.obj['metadata']['labels']['job_id'])
                if job_id in job_ids_to_run:
                    LOG.debug("Found a worker already taking care of id=%s", job_id)
                    job_ids_to_ignore.add(job_id)
                else:
                    # We do not kill jobs that have been completed to keep the logs around. We do
                    # want to kill jobs that are still in the processing stage though.
                    # See states docs http://kubernetes.io/docs/user-guide/pod-states/
                    if pod.running or pod.pending:
                        pods_to_kill.append(pod)
                        job_ids_to_kill.append(job_id)
                    else:
                        LOG.warning("Encountered a Pod that is not ready (running or completed): %s",
                                    pod.obj['metadata']['name'])

        # Take first N jobs
        # Take from pods_to_kill and job_ids_to_kill the first M
        # s.t. resources(M) == resources(N) * 1.1
        jobs_staggered = [j for j in jobs_to_run if j.id not in job_ids_to_ignore][:self.staggering]
        LOG.debug("Staggered jobs: %s", jobs_staggered)

        resources_needed = {'cpu': sum(j.request_cpu for j in jobs_staggered) * self.stagger_factor,
                            'memory': sum(j.request_memory for j in jobs_staggered) * self.stagger_factor,
                            'pods': int(self.staggering * self.stagger_factor)}

        # pods_zipped are the pods zipped with job_ids sorted by id
        # s.t. we can zip them again with the job objects, which are unknown
        pods_zipped = sorted(zip(pods_to_kill, job_ids_to_kill), key=operator.itemgetter(1))
        jobs = Job.select(Job.request_cpu, Job.request_memory, Job.priority) \
                  .where(Job.id.in_(job_ids_to_kill)) \
                  .order_by(Job.id.asc())

        jobs_staggered_to_kill = []
        for (pod, job_id), job in sorted(zip(pods_zipped, jobs), key=lambda j: j[1].priority):
            resources_needed['cpu'] -= job.request_cpu
            resources_needed['memory'] -= job.request_memory
            resources_needed['pods'] -= 1
            jobs_staggered_to_kill.append(job_id)

            LOG.debug("Sacrificing job id=%s", job_id)

            if resources_needed['cpu'] < 0 and resources_needed['memory'] < 0 and resources_needed['pods'] < 0:
                LOG.debug("Collected enough jobs to sacrifice for our staggered jobs")
                break

        LOG.debug("Terminating workers: %s", jobs_staggered_to_kill)
        LOG.debug("Workers running already: %s", job_ids_to_ignore)

        # Kill workers
        def _terminate(job_id):
            LOG.debug("Killing worker for job %s", job_id)
            self.terminate(self._worker_name(job_id))

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(_terminate, jobs_staggered_to_kill)

        # Schedule jobs
        def _schedule(job):
            LOG.debug("Scheduling %s for cs=%s cbn=%s", job.__class__.__name__, job.cs_id,
                        job.cbn_id)
            self.schedule(job)

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(_schedule, jobs_staggered)

        self._kube_resources    # pylint: disable=pointless-statement
