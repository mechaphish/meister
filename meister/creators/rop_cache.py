#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models.job import RopCacheJob

import meister.creators
LOG = meister.creators.LOG.getChild('Cache')


class RopCacheCreator(meister.creators.BaseCreator):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs...")
        for cbn in self.cbns():
            job, _ = RopCacheJob.get_or_create(cbn=cbn, limit_cpu=1, limit_memory=8)
            job.priority = 90  # A rop cache should probably always be created
            LOG.debug("Yielding RopCacheJob for %s", cbn.id)
            yield job
