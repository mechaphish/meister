from collections import defaultdict
from ..scheduler import Scheduler
from crscommon.jobs import RexJob
import crscommon

class RexScheduler(Scheduler):

    def schedule(self):
        # check for new crashing test cases

        out = [ ]

        for b in crscommon.api.get_all_binaries():
            out.extend([RexJob(b, testcase) for testcase in b.crashes])

        return out
