# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import ColorGuardJob 

LOG = meister.creators.LOG.getChild('colorguard')

class RexCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for test in cbn.not_colorguard_traced:
                job = ColorGuardJob(cbn=cbn, payload={'test_id': test.id},
                             limit_cpu=1, limit_memory=10)
                if not ColorGuardJob.queued(job):
                    LOG.debug("Yielding ColorGuardJob for %s with %s", cbn.id, test.id)
                    yield job
