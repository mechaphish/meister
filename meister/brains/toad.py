#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import meister.brains

LOG = meister.brains.LOG.getChild('toad')


class ToadBrain(object):

    def __init__(self):
        pass

    def sort(self, jobs):
        LOG.debug("Sorting jobs...")
        return sorted(self.jobs, key=operator.itemgetter(1), reverse=True)
