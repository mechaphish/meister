#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models.job import ShowmapSyncJob

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
                job = ShowmapSyncJob(cs=cs, limit_cpu=1, limit_time=60 * 10, limit_memory=1024 * 6)
                priority = 100 # we should always try to sync new testcases
                LOG.debug("Yielding FunctionIdentifierJob for %s", cs.name)
                yield (job, priority)
