#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import Round, ShowmapSyncJob

import meister.creators
LOG = meister.creators.LOG.getChild('ShowmapSync')


class ShowmapSyncCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cs in self.challenge_sets():

            if cs.is_multi_cbn:
                LOG.warning("ShowmapSync does not support MultiCBs yet")

            else:
                prev_round = Round.prev_round()
                if prev_round:
                    job = ShowmapSyncJob(cs=cs, payload={"round_id": prev_round.id},
                        limit_cpu=1, limit_time=60 * 10, limit_memory=1024 * 6)

                    priority = 100 # we should always try to sync new testcases
                    LOG.debug("Yielding ShowmapSyncJob for %s, round #%d", cs.name, prev_round.num)
                    yield (job, priority)
