# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import PollSanitizerJob
from farnsworth.models import RawRoundPoll

LOG = meister.creators.LOG.getChild('pollsanitizer')


class NetworkPollSanitizer(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get only un sanitized raw polls to sanitize
        for curr_unsan_poll in RawRoundPoll.select().where(RawRoundPoll.sanitized is False):
            job = PollSanitizerJob(payload={'rrp_id': curr_unsan_poll.id})
            if not PollSanitizerJob.queued(job):
                LOG.debug("Yielding PollSanitizerJob for %s ", curr_unsan_poll.id)
                yield job
