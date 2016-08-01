#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import RawRoundTraffic, RawRoundPoll, ShowmapSyncJob

import meister.creators
LOG = meister.creators.LOG.getChild('showmap_sync')


class ShowmapSyncCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def _jobs(self):
        LOG.debug("Collecting jobs")
        # For each round see if we need to schedule a ShowmapSyncCreator
        for rrt in RawRoundTraffic.select(RawRoundTraffic.id) \
                .where(RawRoundTraffic.processed):

            LOG.debug("RawRoundTraffic #%d has been processed", rrt.id)

            for cs in self.challenge_sets():
                if cs.raw_round_polls.where(RawRoundPoll.raw_round_traffic == rrt).exists():

                    job = ShowmapSyncJob(cs=cs, payload={"rrt_id": rrt.id},
                                         request_cpu=1, request_memory=4096,
                                         limit_memory=8192, limit_time=10 * 60)

                    priority = 100  # We should always try to sync new testcases

                    LOG.debug("Yielding ShowmapSyncJob for %s, rrt #%d", cs.name, rrt.id)
                    yield (job, priority)
