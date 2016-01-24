from ..scheduler import Scheduler
from crscommon.jobs import AFLJob
import crscommon

class AFLScheduler(Scheduler):
    def schedule(self):
        return [ AFLJob(b) for b in crscommon.api.get_all_binaries() ]
