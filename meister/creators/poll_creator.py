#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import PollCreatorJob, Test, ValidPoll

import meister.creators
LOG = meister.creators.LOG.getChild('poll_creator')


class PollCreatorCreator(meister.creators.BaseCreator):
    # we want each CS to have these many polls
    SAFE_NUM_POLLS = 10000

    @property
    def jobs(self):
        for curr_test in Test.select().where(Test.poll_created == False):
            job = PollCreatorJob(cs=curr_test.cs, payload={'test_id': curr_test.id}, limit_cpu=20,
                                 limit_memory=4096*2)
            priority = 20

            # Set high priority only, if there are less polls
            num_poll_available = ValidPoll.select() \
                                          .where(ValidPoll.cs == curr_test.cs) \
                                          .count()
            if num_poll_available < PollCreatorCreator.SAFE_NUM_POLLS:
                priority = 100

            LOG.debug("Creating PollJob for cs %s with test %s ", curr_test.cs.name, curr_test.id)
            yield (job, priority)
