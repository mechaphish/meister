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
            job = PollCreatorJob(cs=curr_test.cs, payload={'test_id': curr_test.id})
            LOG.debug("Creating PollJob for cs %s with test %s ", curr_test.cs.name, curr_test.id)
            # yield job
        return iter(())
