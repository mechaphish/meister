#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models.job import CacheJob

import meister.creators
LOG = meister.creators.LOG.getChild('Cache')


class CacheCreator(meister.creators.BaseCreator):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs...")
        for cs in self.single_cb_challenge_sets():
            job = CacheJob(cs=cs, request_cpu=1, request_memory=8192)
            LOG.debug("Yielding CacheJob for %s", cs.name)
            yield (job, 100)
