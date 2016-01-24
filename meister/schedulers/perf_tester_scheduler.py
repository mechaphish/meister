from ..scheduler import Scheduler
from crscommon.jobs import PerfTesterJob
import crscommon


class PerfTestScheduler(Scheduler):

    @staticmethod
    def get_perf_test_testids(target_binary):
        """

        :param target_binary:
        :return:
        """
        return crscommon.api.get_testcases_for_perfcheck(target_binary.ct_id, target_binary.binary_id)

    def schedule(self):
        to_schedule_jobs = []
        for target_bin in crscommon.api.get_all_binaries():
            for target_test_id in PerfTestScheduler.get_perf_test_testids(target_bin):
                to_schedule_jobs.append(PerfTesterJob(target_bin, target_test_id))
        return to_schedule_jobs
