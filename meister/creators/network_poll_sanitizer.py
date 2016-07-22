#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import NetworkPollSanitizerJob, RawRoundPoll, ValidPoll

import meister.creators
from .poll_creator import PollCreatorCreator
LOG = meister.creators.LOG.getChild('network_poll_sanitizer')


class NetworkPollSanitizerCreator(meister.creators.BaseCreator):

    @property
    def jobs(self):
        for curr_unsan_poll in RawRoundPoll.select().where(RawRoundPoll.sanitized == False):
            # Get the number of polls available for current CS
            job = NetworkPollSanitizerJob(cs=curr_unsan_poll.cs,
                                          payload={'rrp_id': curr_unsan_poll.id},
                                          limit_cpu=20, limit_memory=4096*2)
            priority = 20

            # Set high priority only, if there are less polls
            num_poll_available = ValidPoll.select() \
                                          .where(ValidPoll.cs == curr_unsan_poll.cs) \
                                          .count()
            if num_poll_available < PollCreatorCreator.SAFE_NUM_POLLS:
                priority = 100

            LOG.debug("Creating PollSanitizerJob for %s ", curr_unsan_poll.id)
            yield (job, priority)
