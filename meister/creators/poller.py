# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import PollerJob
from farnsworth.models import Test

LOG = meister.creators.LOG.getChild('poller')


class PollerCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get only those tests, for which polls need to be created.
        for curr_test in Test.select().where(Test.poll_created == False):
            job, _ = PollerJob.get_or_create(cbn=curr_test.cbn,
                                             payload={'test_id': curr_test.id})
            LOG.debug("Creating PollerJob for %s ", curr_test.id)
            # yield job
        return iter(())
