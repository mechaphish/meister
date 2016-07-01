#!/usr/bin/env python

import meister.creators
from farnsworth.models.job import IDSJob

LOG = meister.creators.LOG.getChild('ids')


class IDSCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs")
        for cs in self.challenge_sets():
            job = IDSJob(payload={'cs_id': cs.id}, limit_cpu=1, limit_memory=1, priority=15)
            if not IDSJob.queued(job):
                LOG.debug("Yielding IDSJob for %s", cs.id)
                yield job
