# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import ColorGuardJob, TracerCache

LOG = meister.creators.LOG.getChild('colorguard')

class ColorGuardCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():

            if cbn.tracer_cache.exists():
                LOG.debug("Tracer cache found for %s, scheduling ColorGuard", cbn.name)
                for test in cbn.tests:
                    LOG.debug("ColorGuardJob for %s, test %s being created", cbn.name, test.id)
                    job, _ = ColorGuardJob.get_or_create(cbn=cbn,
                                                         payload={'test_id': test.id},
                                                         limit_cpu=1,
                                                         limit_memory=6)

                    job.priority = 20
                    # if the testcase came from Rex, bump up the priority by four
                    if test.job.worker == "rex":
                        job.priority = 80

                    LOG.debug("Yielding ColorGuardJob for %s with %s", cbn.id, test.id)
                    yield job
            else:
                LOG.debug("No tracer caches for %s, refusing to schedule ColorGuard", cbn.name)
