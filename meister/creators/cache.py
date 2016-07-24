#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models.job import CacheJob

import meister.creators
LOG = meister.creators.LOG.getChild('cache')


class CacheCreator(meister.creators.BaseCreator):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def jobs(self):
        LOG.debug("Collecting jobs...")
        for cs in self.single_cb_challenge_sets():
            # if we have identification results run another one
            if cs.completed_function_identification:
                job = CacheJob(cs=cs, request_cpu=1, request_memory=512, limit_memory=8192,
                               payload={'with_atoi': True})
                yield (job, 100)

            job = CacheJob(cs=cs, request_cpu=1, request_memory=512, limit_memory=8192,
                           payload={'with_atoi': False})
            LOG.debug("Yielding CacheJob for %s", cs.name)
            yield (job, 100)
