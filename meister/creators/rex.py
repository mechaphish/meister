#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import itertools

from farnsworth.models import RexJob, Crash
from peewee import fn

import meister.creators
LOG = meister.creators.LOG.getChild('rex')


class Vulnerability(object):
    IP_OVERWRITE = "ip_overwrite"
    PARTIAL_IP_OVERWRITE = "partial_ip_overwrite"
    UNCONTROLLED_IP_OVERWRITE = "uncontrolled_ip_overwrite"
    BP_OVERWRITE = "bp_overwrite"
    PARTIAL_BP_OVERWRITE = "partial_bp_overwrite"
    WRITE_WHAT_WHERE = "write_what_where"
    WRITE_X_WHERE = "write_x_where"
    # UNCONTROLLED_WRITE is a write where the destination address is uncontrolled
    UNCONTROLLED_WRITE = "uncontrolled_write"
    ARBITRARY_READ = "arbitrary_read"
    NULL_DEREFERENCE = "null_dereference"
    ARBITRARY_TRANSMIT = "arbitrary_transmit"
    ARBITRARY_RECEIVE = "arbitrary_receive"
    UNKNOWN = "unknown"

PRIORITY_MAP = {Vulnerability.IP_OVERWRITE: 100,
                Vulnerability.ARBITRARY_TRANSMIT: 100,
                Vulnerability.PARTIAL_IP_OVERWRITE: 80,
                Vulnerability.ARBITRARY_RECEIVE: 80,
                Vulnerability.ARBITRARY_READ: 75,
                Vulnerability.WRITE_WHAT_WHERE: 50,
                Vulnerability.WRITE_X_WHERE: 25,
                Vulnerability.BP_OVERWRITE: 10,     # doesn't appear to be exploitable in CGC
                Vulnerability.PARTIAL_BP_OVERWRITE: 5,
                Vulnerability.UNCONTROLLED_WRITE: 0,
                Vulnerability.UNCONTROLLED_IP_OVERWRITE: 0,
                Vulnerability.NULL_DEREFERENCE: 0}

# the base Rex priority
BASE_PRIORITY = 10
# the limit of crashes to schedule at a time
FEED_LIMIT = 200

class RexCreator(meister.creators.BaseCreator):

    @staticmethod
    def _filter_non_exploitable(crashes):
        # ignore crashes of kind null_dereference, uncontrolled_ip_overwrite,
        # uncontrolled_write and unknown
        non_exploitable = [Vulnerability.NULL_DEREFERENCE,
                          Vulnerability.UNCONTROLLED_IP_OVERWRITE,
                          Vulnerability.UNCONTROLLED_WRITE,
                          Vulnerability.UNKNOWN]

        # ignore any crashes which are the same crashing pc of an explored, exploited, or leaked input
        # TODO we may just want to lower the priority of these crashes
        return crashes.where(~(Crash.kind << non_exploitable) \
                             & (Crash.triaged != True))

    @staticmethod
    def _normalize_sort(base, ordered_crashes):
        for p, c in enumerate(ordered_crashes):
            yield max(base, 100 - p), c

    @property
    def _jobs(self):
        for cs in self.single_cb_challenge_sets():
            # does this fetch blobs? can we do the filter with the query?
            crashes = self._filter_non_exploitable(cs.crashes)

            encountered_subquery = crashes.select(fn.Distinct(Crash.crash_pc)) \
                                          .where((Crash.explored) | (Crash.exploited))

            categories = dict()
            for vulnerability in PRIORITY_MAP.keys():
                high_priority = crashes.select(Crash.id).where((Crash.kind == vulnerability) \
                    & ~(Crash.crash_pc << encountered_subquery)).order_by(Crash.bb_count.asc())
                low_priority = crashes.select(Crash.id).where((Crash.kind == vulnerability) \
                    & (Crash.crash_pc << encountered_subquery)).order_by(Crash.bb_count.asc())

                if high_priority or low_priority:
                    sliced = itertools.islice(itertools.chain(high_priority, low_priority), FEED_LIMIT)
                    categories[vulnerability] = sliced

            type1_exists = cs.has_type1
            type2_exists = cs.has_type2

            # normalize by ids
            for kind in categories:
                for priority, crash in self._normalize_sort(BASE_PRIORITY, categories[kind]):
                    job = RexJob(cs=cs, payload={'crash_id': crash.id},
                                 request_cpu=1, request_memory=4096,
                                 limit_memory=25600, limit_time=30 * 60)

                    if type1_exists and type2_exists:
                        priority = BASE_PRIORITY

                    # we have type1s? lower the priority of ip_overwrites
                    if type1_exists and crash.kind == 'ip_overwrite':
                        priority = BASE_PRIORITY

                    # we have types2? lower the priority
                    if type2_exists and crash.kind == 'arbitrary_read':
                        priority = BASE_PRIORITY

                    LOG.debug("Yielding RexJob for %s with crash %s priority %d",
                              cs.name, crash.id, priority)

                    yield (job, priority)
