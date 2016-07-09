#!/usr/bin/env python

import meister.creators
from farnsworth.models.job import FunctionIdentifierJob

LOG = meister.creators.LOG.getChild('FunctionIdentifier')

class FunctionIdentifierCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cbn in self.cbns():

            job, _ = FunctionIdentifierJob.get_or_create(cbn=cbn,
                                                         limit_cpu=1,
                                                         limit_time=60 * 10,
                                                         limit_memory=8)

            job.priority = 100 # function identification should always run

            LOG.debug("Yielding FunctionIdentifierJob for %s", cbn.id)
            yield job
