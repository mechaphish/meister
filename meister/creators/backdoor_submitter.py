#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models.job import BackdoorSubmitterJob

import meister.creators
LOG = meister.creators.LOG.getChild('backdoor_submitter')


class BackdoorSubmitterCreator(meister.creators.BaseCreator):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def _jobs(self):
        LOG.debug("Collecting jobs...")
        for cs in self.challenge_sets():
            job = BackdoorSubmitterJob(cs=cs, request_cpu=1, request_memory=512, limit_memory=1024)
            LOG.debug("Yielding BackdoorSubmitterJob for %s", cs.name)
            yield (job, 100)
