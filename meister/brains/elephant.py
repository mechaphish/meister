#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import meister.brains

LOG = meister.brains.LOG.getChild('elephant')


class ElephantBrain(meister.brains.Brain):

    def __init__(self):
        pass

    def _local(job):
        # Local priorities are within a ChallengeSet:
        # - What is more important for this CS right now? A PoV or a RCB?
        return 1.

    def _global(job):
        # Global priorities are for the entire game:
        # - How old is this CS? Must it be retired soon? Is it fresh?
        # - How important is this CS?
        #   - Do we have other unpatched/unexploited CS?
        return 1.

    def _sort(self, jobs):
        jobs = ((j, self._global(j) * self._local(j) * p) for j, p in jobs)
        return sorted(jobs, key=operator.itemgetter(1), reverse=True)
