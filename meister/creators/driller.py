#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models.job import DrillerJob

import meister.creators
LOG = meister.creators.LOG.getChild('driller')

class DrillerCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cs in self.single_cb_challenge_sets():

            if cs.fuzzer_stat is None or cs.fuzzer_stat.last_path is None:
                continue

            # is the fuzzer still working on mutating favorites?
            if not cs.fuzzer_stat.pending_favs > 0:
                LOG.info("AFL has no pending favs, scheduling Driller")
                LOG.debug("Found {} undrilled tests".format(len(cs.undrilled_tests)))
                found_crash = cs.found_crash
                for test in cs.tests:
                    job, _ = DrillerJob.get_or_create(cs=cs,
                                                      limit_cpu=1,
                                                      limit_memory=10,
                                                      limit_time=15 * 60,
                                                      payload={'test_id': test.id})
                    LOG.debug("Yielding DrillerJob for %s with %s", cs.name, test.id)

                    job.priority = 20
                    if not found_crash:
                        job.priority = 100

                    yield job
