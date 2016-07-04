#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import meister.creators
from farnsworth.models import RexJob

LOG = meister.creators.LOG.getChild('rex')


class Vulnerability(object):
    IP_OVERWRITE = "ip_overwrite"
    PARTIAL_IP_OVERWRITE = "partial_ip_overwrite"
    UNCONTROLLED_IP_OVERWRITE = "uncontrolled_ip_overwrite"
    BP_OVERWRITE = "bp_overwrite"
    PARTIAL_BP_OVERWRITE = "partial_bp_overwrite"
    WRITE_WHAT_WHERE = "write_what_where"
    WRITE_X_WHERE = "write_x_where"
    UNCONTROLLED_WRITE = "uncontrolled_write" # a write where the destination address is uncontrolled
    ARBITRARY_READ = "arbitrary_read"
    NULL_DEREFERENCE = "null_dereference"


priority_map = {
        Vulnerability.IP_OVERWRITE: 100,
        Vulnerability.PARTIAL_IP_OVERWRITE: 80,
        Vulnerability.ARBITRARY_READ: 75,
        Vulnerability.WRITE_WHAT_WHERE: 50,
        Vulnerability.WRITE_X_WHERE: 25,
        Vulnerability.BP_OVERWRITE: 10, # doesn't appear to be exploitable in CGC
        Vulnerability.PARTIAL_BP_OVERWRITE: 5,
        Vulnerability.UNCONTROLLED_WRITE: 0,
        Vulnerability.UNCONTROLLED_IP_OVERWRITE: 0,
        Vulnerability.NULL_DEREFERENCE: 0,
        }

class RexCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for crash in cbn.crashes:

                # ignore crashes of kind null_dereference, uncontrolled_ip_overwrite, and uncontrolled_write
                if crash.kind in [Vulnerability.NULL_DEREFERENCE, Vulnerability.UNCONTROLLED_IP_OVERWRITE, \
                        Vulnerability.UNCONTROLLED_WRITE]:
                    continue

                # TODO: in rare cases Rex needs more memory, can we try to handle cases where Rex needs upto 40G?
                job, _ = RexJob.get_or_create(cbn=cbn, payload={'crash_id': crash.id},
                                              limit_cpu=1, limit_memory=10)

                # determine priority
                job.priority = priority_map[crash.kind]

                LOG.debug("Yielding RexJob for %s with %s", cbn.id, crash.id)
                yield job
