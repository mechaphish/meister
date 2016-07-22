#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import NetworkPollCreatorJob
from farnsworth.models import RawRoundTraffic

import meister.creators
LOG = meister.creators.LOG.getChild('network_poll_creator')


class NetworkPollCreatorCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get only unprocessed traffic files and schedule them.
        for curr_round_traffic in RawRoundTraffic.select().where(RawRoundTraffic.processed == False):
            job = NetworkPollCreatorJob(limit_cpu=1, limit_memory=4096*2,
                                        payload={'rrt_id': curr_round_traffic.id})
            priority = 100
            LOG.debug("Creating NetworkPollCreatorJob for %s ", curr_round_traffic.id)
            yield (job, priority)
