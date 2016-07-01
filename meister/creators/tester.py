# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import ChallengeBinaryNode, TesterJob

LOG = meister.creators.LOG.getChild('rex')

class TesterCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in ChallengeBinaryNode.all_descendants():
            for test in cbn.all_tests_for_this_cb:
                job = TesterJob.get_or_create(cbn=cbn,
                                              payload={'test_id': test.id},
                                              limit_cpu=8,
                                              limit_memory=1)
                LOG.debug("Yielding TesterJob for %s with %s", cbn.id, test.id)
                yield job
