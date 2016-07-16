#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import RexJob, Exploit, Crash

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
    UNKNOWN = "unknown"

PRIORITY_MAP = {Vulnerability.IP_OVERWRITE: 100,
                Vulnerability.PARTIAL_IP_OVERWRITE: 80,
                Vulnerability.ARBITRARY_READ: 75,
                Vulnerability.WRITE_WHAT_WHERE: 50,
                Vulnerability.WRITE_X_WHERE: 25,
                Vulnerability.BP_OVERWRITE: 10,     # doesn't appear to be exploitable in CGC
                Vulnerability.PARTIAL_BP_OVERWRITE: 5,
                Vulnerability.UNCONTROLLED_WRITE: 0,
                Vulnerability.UNCONTROLLED_IP_OVERWRITE: 0,
                Vulnerability.NULL_DEREFERENCE: 0}

# the base Rex priority
BASE_PRIORITY = 20


class RexCreator(meister.creators.BaseCreator):

    @staticmethod
    def _exploitable_crashes(crashes):
        # ignore crashes of kind null_dereference, uncontrolled_ip_overwrite,
        # uncontrolled_write and unknown
        non_exploitable = [Vulnerability.NULL_DEREFERENCE,
                          Vulnerability.UNCONTROLLED_IP_OVERWRITE,
                          Vulnerability.UNCONTROLLED_WRITE,
                          Vulnerability.UNKNOWN]

        return crashes.where(~(Crash.kind << non_exploitable) & (Crash.triaged != True))

    @staticmethod
    def _normalize_sort(base, ordered_crashes):
        for p, c in ordered_crashes:
            yield max(base, 100 - p), c

    @property
    def jobs(self):
        for cs in self.single_cb_challenge_sets():
            # does this fetch blobs? can we do the filter with the query?
            crashes = self._exploitable_crashes(cs.crashes)

            categories = dict()
            for vulnerability in PRIORITY_MAP.keys():
                ordered_crashes = crashes.where(Crash.kind == vulnerability).order_by(Crash.created_at.desc())
                if ordered_crashes:
                    categories[vulnerability] = enumerate(ordered_crashes)

            type1_exists = cs.exploits.where(Exploit.pov_type == 'type1').exists()
            type2_exists = cs.exploits.where(Exploit.pov_type == 'type2').exists()

            # normalize by ids
            for kind in categories:
                for priority, crash in self._normalize_sort(BASE_PRIORITY, categories[kind]):
                    # TODO: in rare cases Rex needs more memory, can we try to handle cases where Rex
                    # needs upto 40G?
                    job, _ = RexJob.get_or_create(cs=cs, payload={'crash_id': crash.id},
                                                  limit_cpu=1, limit_memory=10)
                    job.priority = priority

                    # we have type1s? lower the priority of ip_overwrites
                    if type1_exists and crash.kind == 'ip_overwrite':
                            job.priority -= max(BASE_PRIORITY, (100 - BASE_PRIORITY) / 2)

                    if type2_exists and crash.kind == 'arbitrary_read':
                            job.priority -= max(BASE_PRIORITY, (100 - BASE_PRIORITY) / 2)

                    LOG.debug("Yielding RexJob for %s with crash %s priority %d",
                              cs.name, crash.id, job.priority)

                    yield job
