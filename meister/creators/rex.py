#!/usr/bin/env python
# -*- coding: utf-8 -*-

from meister.creators import BaseCreator
from crscommon.jobs import RexJob
import crscommon

class RexCreator(BaseCreator):

    @property
    def jobs(self):
        # check for new crashing test cases

        out = [ ]

        for b in crscommon.api.get_all_binaries():
            out.extend([RexJob(b, testcase) for testcase in b.crashes])

        return out
