#!/usr/bin/env python

import meister.creators
from farnsworth.models.job import WereRabbitJob

LOG = meister.creators.LOG.getChild('WereRabbit')

class WereRabbitCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cbn in self.cbns():
            if len(cbn.crashes) > 0:
                job = WereRabbitJob(cbn=cbn, limit_cpu=4, limit_memory=1)
                if not WereRabbitJob.queued(job):
                    LOG.debug("Yielding AFLJob for %s", cbn.id)
                    yield job
