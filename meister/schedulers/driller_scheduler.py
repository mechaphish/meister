from ..scheduler import Scheduler
from farnsworth_client.models import DrillerJob

class DrillerScheduler(Scheduler):
    def schedule(self, cbn):
        scheduled = [ ]

        for t in cbn.undrilled_tests:
            job = DrillerJob(
                cbn=cbn,
                limit_cpus=1,
                limit_memory=20,
                payload=t
            )

            scheduled.append(super(DrillerScheduler, self).schedule(job))

        return scheduled
