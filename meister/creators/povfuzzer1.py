#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import meister.creators
from farnsworth.models import PovFuzzer1Job
from .rex import Vulnerability

LOG = meister.creators.LOG.getChild('povfuzzer1job')

class PovFuzzer1Creator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for crash in cbn.crashes:

                if crash.kind != Vulnerability.IP_OVERWRITE:
                    continue

                job = PovFuzzer1Job(cbn=cbn, payload={'crash_id': crash.id},
                        limit_cpu=1, limit_memory=10)

                if not PovFuzzer1Job.queued(job):
                    LOG.debug("Yielding PovFuzzer1Job for %s with %s", cbn.id, crash.id)
                    yield job
