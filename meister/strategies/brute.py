#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Brute strategy.

Schedule everything whenver it is available.
"""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division


from requests.exceptions import RequestException

import meister.strategies
from meister.schedulers.afl_scheduler import AFLScheduler

LOG = meister.strategies.LOG.getChild('brute')


class Brute(meister.strategies.BaseStrategy):
    """Brute-force strategy."""

    def __init__(self, *args, **kwargs):
        """Create a brute-force strategy object."""
        super(self.__class__, self).__init__(*args, **kwargs)

    def run(self):
        """Run the brute strategy."""
        while True:
            try:
                LOG.info("Round #%d", self.round)
                for cbn in self.cbns():
                    LOG.debug("Scheduling AFL Job: %s", cbn.name)
                    AFLScheduler().schedule(cbn=cbn, cpus=4, memory=1)
            except RequestException as ex:
                LOG.error("%s", ex)
            self.sleep()
