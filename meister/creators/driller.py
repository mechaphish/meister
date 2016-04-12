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

            check_time = datetime.datetime.now()
            elapsed = check_time - cbn.fuzzer_state.last_path

            # has a path been found in the last minute?
            if elapsed > datetime.timedelta(minutes=1):
                LOG.info("AFL has not found any new paths for 1 minute, scheduling Driller")
                for test in cbn.undrilled_tests:
                    job = DrillerJob(cbn=cbn,
                                     limit_cpus=1, limit_memory=10, limit_time=120,
                                     payload={'test_id': test.id})
                    if not DrillerJob.queued(job):
                        LOG.debug("Yielding AFLJob for %s with %s", cbn.id, test.id)
                        yield job
