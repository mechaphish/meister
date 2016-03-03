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
                LOG.debug("Driller job for %s", cbn.name)
                yield DrillerJob(cbn=cbn, limit_cpus=1, limit_memory=10,
                                 payload={'test_id': test.id})
