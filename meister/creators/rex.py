# -*- coding: utf-8 -*-

from rex import Vulnerability
import meister.creators
from farnsworth.models import RexJob

LOG = meister.creators.LOG.getChild('rex')

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
