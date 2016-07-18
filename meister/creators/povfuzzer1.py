#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from peewee import fn
from farnsworth.models import Crash, PovFuzzer1Job

import meister.creators
from .rex import Vulnerability, BASE_PRIORITY
LOG = meister.creators.LOG.getChild('povfuzzer1job')

class PovFuzzer1Creator(meister.creators.BaseCreator):

    @staticmethod
    def _normalize_sort(base, ordered_crashes):
        for p, c in ordered_crashes:
            yield max(base, 100 - p), c

    @property
    def jobs(self):
        for cs in self.challenge_sets():
            multi_cbn = cs.is_multi_cbn

            # unlike Rex, there's really only one kind of crash we can exploit
            # we do not schedule if we already have a type1 exploit
            if not cs.has_type1:

                if multi_cbn:
                    LOG.warning("MultiCBs as of yet are unsupported, skipping %s", cs.name)

                else:
                    ordered_crashes = cs.crashes.where(Crash.kind == Vulnerability.IP_OVERWRITE)\
                            .order_by(fn.octet_length(Crash.blob).asc())

                    for priority, crash in self._normalize_sort(BASE_PRIORITY, enumerate(ordered_crashes)):

                        job = PovFuzzer1Job(cs=cs, payload={'crash_id': crash.id},
                                            limit_cpu=1, limit_memory=10240)

                        LOG.debug("Yielding PovFuzzer1Job for %s with crash %s priority %d",
                                cs.name, crash.id, priority)

                        yield (job, priority)
