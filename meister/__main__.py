#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run the meister."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import os

import meister.settings

import meister.cgc_client.api
from meister.creators.afl import AFLCreator
from meister.creators.driller import DrillerCreator
from meister.schedulers.brute import BruteScheduler


def main():
    """Run the meister."""
    # Initialize APIs
    cgc = meister.cgc_client.api.from_env()

    # Scheduler strategy
    afl = AFLCreator(cgc)
    driller = DrillerCreator(cgc)
    scheduler = BruteScheduler(cgc=cgc, creators=[afl, driller])
    scheduler.run()

if __name__ == '__main__':
    main()
