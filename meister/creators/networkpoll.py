# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import NetworkPollJob
from farnsworth.models import RawRoundTraffic

LOG = meister.creators.LOG.getChild('networkpoll')


class NetworkPollCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for curr_round_traffic in RawRoundTraffic.all():
            job = NetworkPollJob(payload={'rrt_id': curr_round_traffic.id})
            if not NetworkPollJob.queued(job):
                LOG.debug("Yielding NetworkPollJob for %s ", curr_round_traffic.id)
                yield job
