#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import PovFuzzer2Job

import meister.creators
from .rex import Vulnerability
LOG = meister.creators.LOG.getChild('povfuzzer2job')

class PovFuzzer2Creator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for crash in cbn.crashes:

                if crash.kind != Vulnerability.ARBITRARY_READ:
                    continue

                job, _ = PovFuzzer2Job.get_or_create(cbn=cbn, payload={'crash_id': crash.id},
                                                  limit_cpu=1, limit_memory=10)

                LOG.debug("Yielding PovFuzzer1Job for %s with %s", cbn.id, crash.id)
                yield job
