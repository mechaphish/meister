#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from datetime import datetime, timedelta
from farnsworth.models.job import DrillerJob

import meister.creators
LOG = meister.creators.LOG.getChild('driller')

class DrillerCreator(meister.creators.BaseCreator):
    @property
    def _jobs(self):
        for cs in self.single_cb_challenge_sets():
            if cs.fuzzer_stat is None or cs.fuzzer_stat.last_path is None:
                continue

            id_started = cs.function_identification_started_at

            # if we are assuming AFL will start up, we can also assume identification will start up
            if id_started is None:
                continue

            has_pending_favs = cs.fuzzer_stat.pending_favs
            completed_id = cs.completed_function_identification

            # we drill if...
            #  - AFL no longer has any pending favs
            #  - function identification has completed or if 3 minutes has passed since it's scheduling
            surpassed_threshold = datetime.now() > (id_started + timedelta(minutes=3))
            needs_drilling = has_pending_favs == 0 and (completed_id or surpassed_threshold)

            # is the fuzzer still working on mutating favorites?
            if needs_drilling:
                LOG.info("AFL has no pending favs, scheduling Driller")
                LOG.debug("Found {} undrilled tests".format(len(cs.undrilled_tests)))

                have_exploit = cs.has_type1 or cs.has_type2

                for test in cs.tests:
                    job = DrillerJob(cs=cs, request_cpu=1, request_memory=2048,
                                     limit_memory=10240,
                                     limit_time=15 * 60,
                                     payload={'test_id': test.id})
                    LOG.debug("Yielding DrillerJob for %s with %s", cs.name, test.id)

                    priority = 20
                    if not have_exploit:
                        priority = 95

                    yield (job, priority)
