#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Brute strategy.

Schedule everything whenver it is available.
"""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division


import base64
from os import environ as ENV
from time import sleep

from requests.exceptions import RequestException

from farnsworth_client.models import ChallengeBinaryNode
from meister.strategies import BaseStrategy
from meister.schedulers.afl_scheduler import AFLScheduler


class Brute(BaseStrategy):

    """Brute-force strategy."""

    # pylint: disable=star-args
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
    # pylint: enable=star-args

    def run(self):
        """Run the brute strategy."""
        while True:
            try:
                print("[Meister] Round # {}".format(self.round))
                for cbn in self.cbns():
                    print("Scheduling AFL Job: {}".format(cbn.name))
                    AFLScheduler().schedule(cbn=cbn, cpus=4, memory=1)
            except RequestException as ex:
                print("[Meister] ERROR: {}".format(type(ex)))
            self.sleep()
