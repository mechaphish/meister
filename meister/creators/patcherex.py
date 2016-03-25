#!/usr/bin/env python

import meister.creators
from farnsworth.models.job import PatcherexJob

LOG = meister.creators.LOG.getChild('patcherex')


class PatcherexCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cbn in self.cbns():
            job = PatcherexJob(cbn=cbn, limit_cpus=1, limit_memory=4)
            if not PatcherexJob.queued(job):
                LOG.debug("TEST TEST Yielding PatcherexJob for %s", cbn.id)
                yield job
