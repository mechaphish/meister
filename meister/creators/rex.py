# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import RexJob

LOG = meister.creators.LOG.getChild('rex')

class RexCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for crash in cbn.crashes:
                job = RexJob(cbn=cbn, payload={'crash_id': crash.id},
                             limit_cpu=1, limit_memory=10)
                if not RexJob.queued(job):
                    LOG.debug("Yielding RexJob for %s with %s", cbn.id, crash.id)
                    yield job
