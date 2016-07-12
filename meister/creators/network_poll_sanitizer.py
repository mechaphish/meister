#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import PollSanitizerJob
from farnsworth.models import RawRoundPoll

import meister.creators
LOG = meister.creators.LOG.getChild('pollsanitizer')


class NetworkPollSanitizerCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get only un sanitized raw polls to sanitize
        for curr_unsan_poll in RawRoundPoll.select().where(RawRoundPoll.sanitized == False):
            job, _ = PollSanitizerJob.get_or_create(payload={'rrp_id': curr_unsan_poll.id})
            LOG.debug("Creating PollSanitizerJob for %s ", curr_unsan_poll.id)
            # yield job
        return iter(())
