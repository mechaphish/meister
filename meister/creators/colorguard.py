#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import ColorGuardJob

import meister.creators
from .rex import BASE_PRIORITY
LOG = meister.creators.LOG.getChild('colorguard')


class ColorGuardCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cs in self.challenge_sets():
            if cs.completed_caching or cs.tracer_cache.exists() or cs.is_multi_cbn:
                LOG.debug("Caching complete for %s, scheduling ColorGuard", cs.name)

                if cs.has_circumstantial_type2:
                    LOG.debug("Circumstantial Type2 for Challenge %s already exists"
                            "refusing to schedule ColorGuard" % cs.name)
                    continue

                for test in cs.tests:
                    LOG.debug("ColorGuardJob for %s, test %s being created", cs.name, test.id)
                    # TODO: get naive colorguard support working for multicbs
                    job = ColorGuardJob(cs=cs, payload={'test_id': test.id},
                                        limit_cpu=1, limit_memory=6144)

                    priority = BASE_PRIORITY + 10

                    # testcases found by Rex have the potential to be incredibly powerful POVs
                    # the priority should be the max
                    if test.job.worker == "rex":
                        priority = 100

                    LOG.debug("Yielding ColorGuardJob for %s with %s", cs.name, test.id)
                    yield (job, priority)

            else:
                LOG.debug("Caching incomplete for %s, refusing to schedule ColorGuard", cs.name)
