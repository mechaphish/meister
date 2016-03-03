# -*- coding: utf-8 -*-

from meister.creators import BaseCreator

from farnsworth import RexJob

class RexCreator(BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for crash in cbn.crashes:
                yield RexJob(cbn=cbn, payload={'crash_id': crash.id},
                             limit_cpu=1, limit_memory=10)
