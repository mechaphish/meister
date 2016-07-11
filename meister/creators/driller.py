#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
            if not cbn.fuzzer_stat.pending_favs > 0:
                LOG.info("AFL has no pending favs, scheduling Driller")
                LOG.debug("Found {} undrilled tests".format(len(cbn.undrilled_tests)))
                for test in cbn.tests:
                    job, _ = DrillerJob.get_or_create(cbn=cbn,
                                                      limit_cpu=1,
                                                      limit_memory=10,
                                                      limit_time=15 * 60,
                                                      payload={'test_id': test.id})
                    LOG.debug("Yielding DrillerJob for %s with %s", cbn.id, test.id)

                    job.priority = 20
                    if not cbn.found_crash:
                        job.priority = 100

                    yield job
