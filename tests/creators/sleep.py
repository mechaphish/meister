#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time

from farnsworth.models.job import IDSJob

import meister.creators
LOG = meister.creators.LOG.getChild('sleeper')


class SleepCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def _jobs(self):
        LOG.debug("Collecting jobs")
        for cs in range(1, 5):
            job = IDSJob(payload={'cs_id': cs}, request_cpu=1, request_memory=1024)
            LOG.debug("Yielding for SleepCreator %s", cs)
            yield (job, 15)
            time.sleep(10)
