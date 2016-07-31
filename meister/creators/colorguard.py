#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import ColorGuardJob

import meister.creators
from .rex import BASE_PRIORITY
LOG = meister.creators.LOG.getChild('colorguard')


class ColorGuardCreator(meister.creators.BaseCreator):
    @property
    def _jobs(self):
        for cs in self.challenge_sets():
            found_crash_for_cs = cs.found_crash
            if cs.is_multi_cbn:
                LOG.warning("ColorGuard does not support MultiCBs refusing to schedule")

            elif cs.completed_caching or cs.tracer_cache.exists():
                LOG.debug("Caching complete for %s, scheduling ColorGuard", cs.name)
                if cs.has_circumstantial_type2:
                    LOG.debug("Circumstantial Type2 for Challenge %s already exists"
                            "refusing to schedule ColorGuard" % cs.name)
                    continue

                for test in cs.tests:
                    LOG.debug("ColorGuardJob for %s, test %s being created", cs.name, test.id)
                    job = ColorGuardJob(cs=cs, payload={'crash': False, 'id': test.id},
                                        request_cpu=1, request_memory=2048,
                                        limit_memory=10240,
                                        limit_time=10 * 60)

                    priority = BASE_PRIORITY + 10

                    # if there's no crash for a CS, more likely there's a leak.
                    # this is a dumb hueristic, but I believe it adds value
                    if not found_crash_for_cs:
                        priority = 70

                    # testcases found by Rex have the potential to be incredibly powerful POVs
                    # the priority should be the max
                    if test.job.worker == "rex":
                        priority = 100

                    LOG.debug("Yielding ColorGuardJob for %s with %s", cs.name, test.id)
                    yield (job, priority)

                for crash in cs.crashes:
                    LOG.debug("ColorGuardJobs for %s, crash %s being created", cs.name, test.id)
                    job = ColorGuardJob(cs=cs, payload={'crash': True, 'id': crash.id},
                                        request_cpu=1, request_memory=2048,
                                        limit_memory=10240,
                                        limit_time=10 * 60)

                    # because AFL has a harder time distinguishing between interesting crashes
                    # we give these a lower priority
                    priority = BASE_PRIORITY + 5

                    LOG.debug("Yielding ColorGuardJob for %s with crash %s", cs.name, crash.id)
                    yield (job, priority)

            else:
                LOG.debug("Caching incomplete for %s, refusing to schedule ColorGuard", cs.name)
