#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import operator

import meister.brains

LOG = meister.brains.LOG.getChild('elephant')


class ElephantBrain(meister.brains.Brain):

    def _sanitize_component(self, job, priority):
        if priority > 100:
            LOG.warning('Job id=%d has priority > 100 at p=%d, setting to 100', job.id, priority)
            return 100
        elif priority < 0:
            return 0
        else:
            return priority

    def _local(self, job):
        # Local priorities are within a ChallengeSet:
        # - What is more important for this CS right now? A PoV or a RCB?
        return 1.

    def _global(self, job):
        # Global priorities are for the entire game:
        # - How old is this CS? Must it be retired soon? Is it fresh?
        # - How important is this CS?
        #   - Do we have other unpatched/unexploited CS?
        return 1.

    def _sort(self, jobs):
        jobs = ((j, int(self._global(j) * self._local(j) * self._sanitize_component(p)))
                 for j, p in jobs)
        return sorted(jobs, key=operator.itemgetter(1), reverse=True)
