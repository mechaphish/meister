#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literal

from farnsworth.models.job import (CBTesterJob,
                                   NetworkPollCreatorJob,
                                   NetworkPollSanitizerJob,
                                   PovTesterJob)

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
                              NetworkPollSanitizerJob
                              PovTesterJob]

        # Filter jobs that need to be merged and those that are passed
        # through. TesterJobs are per ChallengeSet.
        jobs_to_merge, jobs_new = defaultdict(defaultdict(list)), []
        for job, priority in jobs:
            for job_type in job_types_to_merge:
                if isinstance(job, job_type):
                    # Per ChallengeSet per Job type
                    jobs_to_merge[job.cs][job_type].append((job, priority))
                else:
                    jobs_new.append((job, priority))

        # Merge jobs, to have enough resources, we assign the maximum
        # requested resources to the overall TesterJob.
        limit_cpu = Job.limit_cpu.default,
        limit_memory = Job.limit_memory.default
        limit_time = Job.limit_time.default
        priority = 0
        for cs, job_type__jobs in jobs_to_merge.items():
            # We are doing this manually instead of through max(key=)
            # because it would iterate 3 times over it instead.
            for job_type, jobs in job_type__jobs.items():
                for job, job_priority in jobs:
                    if limit_cpu is not None:
                        limit_cpu = max(limit_cpu, job.limit_cpu)

                    if limit_memory is not None:
                        limit_memory = max(limit_memory, job.limit_memory)

                    if limit_time is not None:
                        limit_time = max(limit_time, job.limit_time)

                    priority = max(priority, job_priority)

                job = job_type(cs=cs, limit_cpu=limit_cpu, limit_memory=limit_memory)
                jobs_new.append((job, priority))

        return self._sort(jobs_new)
