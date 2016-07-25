#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models.job import AFLJob

import meister.creators
LOG = meister.creators.LOG.getChild('AFL')


class AFLCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def _jobs(self):
        LOG.debug("Collecting jobs")
        for cs in self.challenge_sets():
            job = AFLJob(cs=cs, request_cpu=8, request_memory=4096, limit_memory=8192)
            LOG.debug("Yielding AFLJob for %s", cs.name)
            yield (job, 100)
