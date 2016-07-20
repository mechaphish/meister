#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import meister.brains

LOG = meister.brains.LOG.getChild('toad')


class ToadBrain(meister.brains.Brain):

    def _sort(self, jobs):
        LOG.debug("Sorting jobs...")
        return sorted(jobs, key=operator.itemgetter(1), reverse=True)
