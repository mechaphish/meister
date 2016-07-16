#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import ChallengeBinaryNode, TesterJob

import meister.creators
LOG = meister.creators.LOG.getChild('rex')

class TesterCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in ChallengeBinaryNode.all_descendants():
            for test in cbn.all_tests_for_this_cb:
                job = TesterJob(cbn=cbn, payload={'test_id': test.id},
                                limit_cpu=8, limit_memory=1024)
                LOG.debug("Creating TesterJob for %s with %s", cbn.id, test.id)
                # yield job
        return iter(())
