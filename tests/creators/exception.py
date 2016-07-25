#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models.job import IDSJob

import meister.creators
LOG = meister.creators.LOG.getChild('sleeper')


class ExceptionCreator(meister.creators.BaseCreator):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def _jobs(self):
        LOG.debug("Collecting jobs")
        raise Exception("Oh my god, an exception! I failed!")
