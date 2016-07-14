#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import ColorGuardJob

import meister.creators
LOG = meister.creators.LOG.getChild('colorguard')

class ColorGuardCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():

            if cbn.completed_caching or cbn.tracer_cache.exists():
                LOG.debug("Caching complete for %s, scheduling ColorGuard", cbn.name)
                for test in cbn.tests:
                    LOG.debug("ColorGuardJob for %s, test %s being created", cbn.name, test.id)
                    job, _ = ColorGuardJob.get_or_create(cbn=cbn,
                                                         payload={'test_id': test.id},
                                                         limit_cpu=1,
                                                         limit_memory=6)

                    job.priority = 20

                    # testcases found by Rex have the potential to be incredibly powerful POVs
                    # the priority should be the max
                    if test.job.worker == "rex":
                        job.priority = 100

                    LOG.debug("Yielding ColorGuardJob for %s with %s", cbn.id, test.id)
                    yield job

            else:
                LOG.debug("Caching incomplete for %s, refusing to schedule ColorGuard", cbn.name)
