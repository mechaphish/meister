#!/usr/bin/env python
# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models.job import DrillerJob

LOG = meister.creators.LOG.getChild('driller')

class DrillerCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for test in cbn.undrilled_tests:
                job = DrillerJob(cbn=cbn, limit_cpus=1, limit_memory=10,
                                 payload={'test_id': test.id})
                if not DrillerJob.queued(job):
                    LOG.debug("Yielding AFLJob for %s with %s", cbn.id, test.id)
                    yield job
