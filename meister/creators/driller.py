#!/usr/bin/env python
# -*- coding: utf-8 -*-

from meister.creators import BaseCreator
from farnsworth_client.models import DrillerJob


class DrillerCreator(BaseCreator):
    @property
    def jobs(self):
        for cbn in self.cbns():
            for test in cbn.undrilled_tests:
                yield DrillerJob(cbn=cbn, limit_cpus=1, limit_memory=20,
                                 payload=test)
