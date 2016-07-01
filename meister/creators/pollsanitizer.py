# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import PollSanitizerJob
from farnsworth.models import RawRoundPoll

LOG = meister.creators.LOG.getChild('pollsanitizer')


class NetworkPollSanitizerCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get only un sanitized raw polls to sanitize
        for curr_unsan_poll in RawRoundPoll.select().where(RawRoundPoll.sanitized == False):
            job = PollSanitizerJob.get_or_create(limit_cpu=-1, limit_memory=-1,
                                                 payload={'rrp_id': curr_unsan_poll.id})
            LOG.debug("Yielding PollSanitizerJob for %s ", curr_unsan_poll.id)
            yield job
