#!/usr/bin/env python

import meister.creators
from farnsworth.models.job import CacheJob

LOG = meister.creators.LOG.getChild('Cache')


class CacheCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cbn in self.cbns():
            job, _ = CacheJob.get_or_create(cbn=cbn, limit_cpu=1, limit_memory=8)
            job.priority = 100 # A cache should always be created
            LOG.debug("Yielding CacheJob for %s", cbn.id)
            yield job
