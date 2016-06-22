# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import PollerJob
from farnsworth.models import Test

LOG = meister.creators.LOG.getChild('poller')


class PollCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get only those tests, for which polls need to be created.
        for curr_test in Test.select().where(Test.poll_created is False):
            job = PollerJob(payload={'test_id': curr_test.id})
            if not PollerJob.queued(job):
                LOG.debug("Yielding PollerJob for %s ", curr_test.id)
                yield job
