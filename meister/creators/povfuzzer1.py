#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import PovFuzzer1Job

import meister.creators
from .rex import Vulnerability
LOG = meister.creators.LOG.getChild('povfuzzer1job')

class PovFuzzer1Creator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cs in self.challenge_sets():
            for crash in cs.crashes:

                if not cs.is_multi_cbn and crash.kind != Vulnerability.IP_OVERWRITE:
                    continue

                job, _ = PovFuzzer1Job.get_or_create(cs=cs, payload={'crash_id': crash.id},
                                                     limit_cpu=1, limit_memory=10)

                LOG.debug("Yielding PovFuzzer1Job for %s with crash %s", cs.name, crash.id)
                yield job
