# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import ColorGuardJob

LOG = meister.creators.LOG.getChild('colorguard')

class ColorGuardCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            LOG.debug("For cbn %s there are %d tests", cbn.id, len(cbn.not_colorguard_traced))
            for test in cbn.not_colorguard_traced:
                LOG.debug("ColorGuardJob for cbn %s, test %s being created", cbn.id, test.id)
                job = ColorGuardJob.get_or_create(cbn=cbn, payload={'test_id': test.id},
                                                  limit_cpu=1, limit_memory=6)
                LOG.debug("Yielding ColorGuardJob for %s with %s", cbn.id, test.id)
                yield job
