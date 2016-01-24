from ..scheduler import Scheduler
from crscommon.jobs import PerfTesterJob
import crscommon


class PerfTestScheduler(Scheduler):

    def schedule(self):
        return [PerfTesterJob(b) for b in crscommon.api.get_all_binaries()]
