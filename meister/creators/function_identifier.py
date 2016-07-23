#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models.job import FunctionIdentifierJob

import meister.creators
LOG = meister.creators.LOG.getChild('FunctionIdentifier')


class FunctionIdentifierCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cs in self.single_cb_challenge_sets():
            job = FunctionIdentifierJob(cs=cs, request_cpu=1, limit_time=60 * 10, request_memory=8192)
            priority = 100 # function identification should always run
            LOG.debug("Yielding FunctionIdentifierJob for %s", cs.name)
            yield (job, priority)
