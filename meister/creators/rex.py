#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import meister.creators
from farnsworth.models import RexJob, PovFuzzer1Job, PovFuzzer2Job

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


class RexCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for crash in cbn.crashes:

                # ignore crashes of kind null_dereference, uncontrolled_ip_overwrite, and uncontrolled_write
                if crash.crash_kind in [Vulnerability.NULL_DEREFERENCE, Vulnerability.UNCONTROLLED_IP_OVERWRITE, \
                        Vulnerability.UNCONTROLLED_WRITE]:
                    continue

                # TODO: in rare cases Rex needs more memory, can we try to handle cases where Rex needs upto 40G?
                job = RexJob(cbn=cbn, payload={'crash_id': crash.id},
                             limit_cpu=1, limit_memory=10)

                if not RexJob.queued(job):
                    LOG.debug("Yielding RexJob for %s with %s", cbn.id, crash.id)
                    yield job

                if crash.crash_kind in [Vulnerability.IP_OVERWRITE]:
                    # TODO: I want to make this 8 cpu's, but we need to fix it so we don't use up all resources by
                    # scheduling a million jobs
                    job = PovFuzzer1Job(cbn=cbn, payload={'crash_id': crash.id},
                                        limit_cpu=1, limit_memory=10)
                    yield job

                if crash.crash_kind in [Vulnerability.ARBITRARY_READ]:
                    # TODO: I want to make this 8 cpu's, but we need to fix it so we don't use up all resources by
                    # scheduling a million jobs
                    job = PovFuzzer2Job(cbn=cbn, payload={'crash_id': crash.id},
                                        limit_cpu=1, limit_memory=10)
                    yield job
