#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models.job import WereRabbitJob

import meister.creators
LOG = meister.creators.LOG.getChild('WereRabbit')


class WereRabbitCreator(meister.creators.BaseCreator):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cs in self.challenge_sets():
            if len(cs.crashes) > 0:
                job = WereRabbitJob(cs=cs, limit_cpu=4, limit_memory=4096)
                priority = 100 # There should *ALWAYS* be one WereRabbit job running if we have a crash
                LOG.debug("Yielding WereRabbitJob for %s", cs.name)

                yield (job, priority)
