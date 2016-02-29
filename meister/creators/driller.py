#!/usr/bin/env python
# -*- coding: utf-8 -*-

from meister.creators import BaseCreator
import crscommon

class DrillerCreator(BaseCreator):
    def schedule(self):
        return [crscommon.jobs.DrillerJob(t.binary, t) for t in t.binary.undrilled_testcases]
