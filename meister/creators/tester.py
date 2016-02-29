#!/usr/bin/env python
# -*- coding: utf-8 -*-

from meister.creators import BaseCreator

from crscommon.jobs import TesterJob
import crscommon

class TestCreator(BaseCreator):

    @property
    def jobs(self):
        all_jobs = []
        for b in crscommon.api.get_all_binaries():
            for testcase_id in crscommon.api.get_testcases_for_testing(b.ct.id, b.binary_id):
                all_jobs.append(TesterJob(b, testcase_id))
        return all_jobs

