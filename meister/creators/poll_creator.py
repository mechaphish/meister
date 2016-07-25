#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import PollCreatorJob, Test, ValidPoll, ChallengeSet

import meister.creators
LOG = meister.creators.LOG.getChild('poll_creator')


class PollCreatorCreator(meister.creators.BaseCreator):
    # we want each CS to have these many polls
    SAFE_NUM_POLLS = 10000
    # reasonable number of polls
    RESONABLE_NUM_POLLS = 1000

    @property
    def jobs(self):
        # iterate only for currently active ChallengeSets
        for curr_cs in ChallengeSet.fielded_in_round():
            for curr_test in Test.select().where((Test.poll_created == False) & (Test.cs == curr_cs)):
                job = PollCreatorJob(cs=curr_test.cs, payload={'test_id': curr_test.id}, request_cpu=20,
                                     request_memory=4096*2)
                priority = 20

                # Set high priority only, if there are less polls
                num_poll_available = ValidPoll.select() \
                                              .where(ValidPoll.cs == curr_test.cs) \
                                              .count()
                if num_poll_available < PollCreatorCreator.SAFE_NUM_POLLS:
                    priority = ((PollCreatorCreator.SAFE_NUM_POLLS - num_poll_available) * 100) / \
                               (PollCreatorCreator.SAFE_NUM_POLLS - PollCreatorCreator.RESONABLE_NUM_POLLS)

                # sanity, bound priority values
                if priority < 0:
                    priority = 0
                if priority > 100:
                    priority = 100

                LOG.debug("Creating PollJob for cs %s with test %s ", curr_test.cs.name, curr_test.id)
                yield (job, priority)
