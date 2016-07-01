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
            job = PollerJob.get_or_create(cbn=curr_test.cbn, limit_cpu=-1,
                                          limit_memory=-1,
                                          payload={'test_id': curr_test.id})
            LOG.debug("Yielding PollerJob for %s ", curr_test.id)
            yield job
