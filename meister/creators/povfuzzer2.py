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
        for cs in self.challenge_sets():
            multi_cbn = cs.is_multi_cbn
            for crash in cs.crashes:
                if not multi_cbn and crash.kind != Vulnerability.ARBITRARY_READ:
                    continue

                job = PovFuzzer2Job(cs=cs, payload={'crash_id': crash.id},
                                    limit_cpu=1, limit_memory=10240)

                LOG.debug("Yielding PovFuzzer1Job for %s with crash %s", cs.name, crash.id)
                yield (job, 0)
