#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import PollCreatorJob
from farnsworth.models import Test

import meister.creators
LOG = meister.creators.LOG.getChild('poll_creator')


class PollCreatorCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get only those tests, for which polls need to be created.
        for curr_test in Test.select().where(Test.poll_created == False):
            job, _ = PollCreatorJob.get_or_create(cbn=curr_test.cbn,
                                           payload={'test_id': curr_test.id})
            LOG.debug("Creating PollJob for %s ", curr_test.id)
            # yield job
        return iter(())
