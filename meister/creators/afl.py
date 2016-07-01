#!/usr/bin/env python

import meister.creators
from farnsworth.models.job import AFLJob

LOG = meister.creators.LOG.getChild('AFL')


class AFLCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cbn in self.cbns():
            job = AFLJob.get_or_create(cbn=cbn, limit_cpu=8, limit_memory=4)
            LOG.debug("Yielding AFLJob for %s", cbn.id)
            yield job
