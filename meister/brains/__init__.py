#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from collections import defaultdict

import farnsworth.config
from farnsworth.models.job import (CBTesterJob,
                                   NetworkPollCreatorJob,
                                   NetworkPollSanitizerJob,
                                   PovTesterJob,
                                   PollCreatorJob,
                                   TesterJob)

import meister.log

LOG = meister.log.LOG.getChild('brains')


class Brain(object):

    def __init__(self):
        pass

    def _sort(self, jobs):
        raise NotImplementedError("_sort must be implemented by a brain")

    def sort(self, jobs):
        # Merge jobs
        job_types_to_merge = [CBTesterJob,
                              NetworkPollCreatorJob,
                              NetworkPollSanitizerJob,
                              PovTesterJob,
                              PollCreatorJob]

        # Filter jobs that need to be merged and those that are passed
        # through. TesterJobs are per ChallengeSet.
        jobs_to_merge, jobs_new = defaultdict(lambda: defaultdict(list)), []
        for job, priority in jobs:
            to_merge = False
            for job_type in job_types_to_merge:
                if isinstance(job, job_type):
                    # Per ChallengeSet per Job type
                    jobs_to_merge[job.cs][job_type].append((job, priority))
                    to_merge = True

            if not to_merge:
                jobs_new.append((job, priority))

        # Merge jobs, to have enough resources, we assign the maximum
        # requested resources to the overall TesterJob.
        # We want this as an atomic transaction because we are doing a
        # lot of get_or_create()
        with farnsworth.config.master_db.atomic():
            for cs, job_type__jobs in jobs_to_merge.items():
                # We are doing this manually instead of through
                # max(key=) because it would iterate 3x over it instead.
                for job_type, jobs in job_type__jobs.items():
                    request_cpu = job_type.request_cpu.default
                    request_memory = job_type.request_memory.default
                    limit_time = job_type.limit_time.default
                    priority = 0

                    for job, job_priority in jobs:
                        if request_cpu is not None:
                            request_cpu = max(request_cpu, job.request_cpu)

                        if request_memory is not None:
                            request_memory = max(request_memory, job.request_memory)

                        if limit_time is not None:
                            limit_time = max(limit_time, job.limit_time)

                        priority = max(priority, job_priority)

                        # Save object to DB so the worker can access it
                        kwargs = {df.name: getattr(job, df.name) for df in job.dirty_fields}
                        job_type.get_or_create(**kwargs)

                    # Add meta job with proper payload to queue
                    job = TesterJob(cs=cs, request_cpu=request_cpu, request_memory=request_memory,
                                    payload={'type': job_type.worker.default})
                    jobs_new.append((job, priority))

        return self._sort(jobs_new)
