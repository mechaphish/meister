#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models.job import BackdoorSubmitterJob

import meister.creators
LOG = meister.creators.LOG.getChild('Cache')


class BackdoorSubmitterCreator(meister.creators.BaseCreator):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs...")
        for cs in self.challenge_sets():
            job = BackdoorSubmitterJob(cs=cs, request_cpu=1, request_memory=128, limit_memory=128)
            LOG.debug("Yielding BackdoorSubmitterJob for %s", cs.name)
            yield (job, 100)
