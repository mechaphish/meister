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
        for cbn in self.cbns():
            if len(cbn.crashes) > 0:
                job, _ = WereRabbitJob.get_or_create(cbn=cbn,
                                                     limit_cpu=4,
                                                     limit_memory=4)

                job.priority = 100 # There should *ALWAYS* be one WereRabbit job running if we have a crash
                LOG.debug("Yielding WereRabbitJob for %s", cbn.id)

                yield job
