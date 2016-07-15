#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import PatchPerformanceJob, Round

import meister.creators
LOG = meister.creators.LOG.getChild('patch_performance')


class PatchPerformanceCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get all current valid ChallengeSets and schedule them.
        # passing round id takes care of not generating duplicates in a round for a cs.
        for curr_cs in self.challenge_sets():
            curr_round = Round.current_round()
            job, _ = PatchPerformanceJob.get_or_create(cs=curr_cs,
                                                       limit_cpu=1,
                                                       limit_memory=2,
                                                       payload={'round_id': curr_round.id})
            job.priority = 50
            LOG.debug("Creating PatchPerformanceCreator for CS %s and Round %s ", curr_cs.name, curr_round.num)
            yield job
