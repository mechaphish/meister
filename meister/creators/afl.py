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
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cs in self.challenge_sets():

            job, _ = AFLJob.get_or_create(cs=cs, limit_cpu=8, limit_memory=4)

            job.priority = 100 # There should *ALWAYS* be one AFL job running per challenge
            LOG.debug("Yielding AFLJob for %s", cs.name)

            yield job
