#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import Crash, Test, ColorGuardJob

import meister.creators
from .rex import BASE_PRIORITY
LOG = meister.creators.LOG.getChild('colorguard')


class ColorGuardCreator(meister.creators.BaseCreator):
    @staticmethod
    def _normalize_sort(base, top, ordered_items):
        for p, c in enumerate(ordered_items):
            yield max(base, top - p), c

    @property
    def _jobs(self):
        for cs in self.challenge_sets():
            found_crash_for_cs = cs.found_crash
            if cs.is_multi_cbn:
                LOG.warning("ColorGuard does not support MultiCBs refusing to schedule")

            elif cs.completed_caching or cs.tracer_cache.exists():
                LOG.debug("Caching complete for %s, scheduling ColorGuard", cs.name)
                has_circumstantial_type2 = cs.has_circumstantial_type2

                if has_circumstantial_type2:
                    LOG.debug("Circumstantial Type2 for Challenge %s already exists "
                              "lowering priority of ColorGuard", cs.name)

                max_priority = BASE_PRIORITY + 10 if found_crash_for_cs else 70
                tests = cs.tests.order_by(Test.created_at.asc())
                tests_by_priority = self._normalize_sort(BASE_PRIORITY + 5,
                                                         max_priority,
                                                         tests)
                for priority, test in tests_by_priority:
                    LOG.debug("ColorGuardJob for %s, test %s being created", cs.name, test.id)
                    job = ColorGuardJob(cs=cs,
                                        payload={'crash': False, 'id': test.id},
                                        request_cpu=1,
                                        request_memory=2048,
                                        limit_memory=10240,
                                        limit_time=10 * 60)

                    # testcases found by Rex have the potential to be incredibly powerful POVs
                    # the priority should be the max
                    if test.job.worker == "rex":
                        priority = 100

                    if has_circumstantial_type2:
                        priority = max(BASE_PRIORITY, priority - 70)

                    LOG.debug("Yielding ColorGuardJob for %s with %s, priority %d", cs.name, test.id, priority)
                    yield (job, priority)

                crashes = cs.crashes.order_by(Crash.bb_count.asc())
                crashes_by_priority = self._normalize_sort(BASE_PRIORITY,
                                                           BASE_PRIORITY + 5,
                                                           crashes)
                for priority, crash in crashes_by_priority:
                    LOG.debug("ColorGuardJobs for %s, crash %s being created", cs.name, crash.id)
                    job = ColorGuardJob(cs=cs,
                                        payload={'crash': True, 'id': crash.id},
                                        request_cpu=1,
                                        request_memory=2048,
                                        limit_memory=10240,
                                        limit_time=10 * 60)

                    # because AFL has a harder time distinguishing between interesting crashes
                    # we give these a lower priority
                    priority = BASE_PRIORITY + 5

                    if has_circumstantial_type2:
                        priority = BASE_PRIORITY

                    LOG.debug("Yielding ColorGuardJob for %s with crash %s, priority %d",
                              cs.name, crash.id, priority)
                    yield (job, priority)

            else:
                LOG.debug("Caching incomplete for %s, refusing to schedule ColorGuard", cs.name)
