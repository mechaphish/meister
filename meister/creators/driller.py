#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import meister.creators
from farnsworth.models.job import DrillerJob

LOG = meister.creators.LOG.getChild('driller')

class DrillerCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():

            if cbn.fuzzer_stat is None or cbn.fuzzer_stat.last_path is None:
                continue

            # is the fuzzer still working on mutating favorites?
            if not (cbn.fuzzer_stat.pending_favs > 0):
                LOG.info("AFL has not found any new paths for 1 minute, scheduling Driller")
                for test in cbn.undrilled_tests:
                    job = DrillerJob(cbn=cbn,
                                     limit_cpus=1, limit_memory=10, limit_time=120,
                                     payload={'test_id': test.id})
                    if not DrillerJob.queued(job):
                        LOG.debug("Yielding DrillerJob for %s with %s", cbn.id, test.id)
                        yield job
