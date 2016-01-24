from ..scheduler import Scheduler
import crscommon

class DrillerScheduler(Scheduler):
    def schedule(self):
        return [ crscommon.jobs.DrillerJob(t.binary, t) for t in t.binary.undrilled_testcases ]
