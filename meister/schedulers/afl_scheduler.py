from ..scheduler import Scheduler
from farnsworth_client.models import AFLJob

class AFLScheduler(Scheduler):
    def schedule(self, cbn, cpus = 4, memory = 1):
        job = AFLJob(
            cbn = cbn,
            limit_cpu = cpus,
            limit_memory = memory,
            payload = cbn, # FIXME: is this really necessary?
        )
        return super(AFLScheduler, self).schedule(job)
