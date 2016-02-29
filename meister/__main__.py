#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run the meister."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import os

import meister.settings

from farnsworth_client.api import API as ProfAPI
import meister.cgc_client.api
from meister.creators.afl import AFLCreator
from meister.schedulers.brute import BruteScheduler


def main():
    """Run the meister."""
    # Initialize APIs
    cgc = meister.cgc_client.api.from_env()
    prof_url = "http://{}:{}".format(os.environ['FARNSWORTH_SERVICE_HOST'],
                                     os.environ['FARNSWORTH_SERVICE_PORT'])
    ProfAPI.init(prof_url)

    # Scheduler strategy
    afl = AFLCreator(cgc)
    scheduler = BruteScheduler(cgc=cgc, creators=[afl])
    scheduler.run()

if __name__ == "__main__":
    main()
