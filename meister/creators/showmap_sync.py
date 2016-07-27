#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import RawRoundTraffic, Round, ShowmapSyncJob

import meister.creators
LOG = meister.creators.LOG.getChild('showmap_sync')


class ShowmapSyncCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def _jobs(self):
        LOG.debug("Collecting jobs")
        # For each round see if we need to schedule a ShowmapSyncCreator
        for rnd in Round.select():
            # Only work on raw round polls which which come from processed rounds
            if not rnd.raw_round_traffics.where(RawRoundTraffic.processed == False).exists():
                LOG.debug("All of round #%d's traffic has been processed", rnd.num)
                for cs in self.challenge_sets():

                    if cs.raw_round_polls.join(Round) \
                            .where(Round.id == rnd.id) \
                            .exists():

                        job = ShowmapSyncJob(cs=cs, payload={"round_id": rnd.id},
                                             request_cpu=1, request_memory=4096,
                                             limit_memory=8192, limit_time=10 * 60)
                        priority = 100  # We should always try to sync new testcases

                        LOG.debug("Yielding ShowmapSyncJob for %s, round #%d", cs.name, rnd.num)
                        yield (job, priority)
            else:
                LOG.debug("Some of round #%d's traffic is unprocessed, skipping", rnd.num)
