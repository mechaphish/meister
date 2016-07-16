#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models.job import PatcherexJob

import meister.creators
LOG = meister.creators.LOG.getChild('patcherex')


class PatcherexCreator(meister.creators.BaseCreator):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cbn in self.cbns():
            for patch_type in PatcherexJob.PATCH_TYPES:
                job = PatcherexJob(cbn=cbn, payload={'patch_type': patch_type}
                                   limit_cpu=1, limit_memory=10240)
                LOG.debug("Yielding PatcherexJob for %s", cbn.name)
                yield (job, 500)
