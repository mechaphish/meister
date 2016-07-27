#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import Crash, PovFuzzer2Job
from peewee import fn

import meister.creators
from .rex import Vulnerability, BASE_PRIORITY
LOG = meister.creators.LOG.getChild('povfuzzer2')


class PovFuzzer2Creator(meister.creators.BaseCreator):

    @staticmethod
    def _normalize_sort(base, ordered_crashes):
        for p, c in ordered_crashes:
            yield max(base, 100 - p), c

    @property
    def _jobs(self):
        for cs in self.challenge_sets():
            if not cs.has_type2:
                ordered_crashes = cs.crashes.where(Crash.kind == Vulnerability.ARBITRARY_READ) \
                                            .order_by(fn.octet_length(Crash.blob).asc())

                for priority, crash in self._normalize_sort(BASE_PRIORITY, enumerate(ordered_crashes)):
                    job = PovFuzzer2Job(cs=cs, payload={'crash_id': crash.id},
                                        request_cpu=1, limit_memory=2048,
                                        limit_time=5 * 60)
                    LOG.debug("Yielding PovFuzzer2Job for %s with crash %s priority %d",
                              cs.name, crash.id, priority)
                    yield (job, priority)
