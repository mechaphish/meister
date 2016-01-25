from collections import defaultdict
from ..scheduler import Scheduler
from crscommon.jobs import PwnrexJob
import crscommon

class PwnrexScheduler(Scheduler):

    def schedule(self):
        # check for new replay attack

        out = []

        for b in crscommon.api.get_all_binaries():
            for team in crscommon.api.get_all_teams():
                out.append(PwnrexJob(b, b.pcaps(team, crscommon.api.get_current_round())))

        return out
