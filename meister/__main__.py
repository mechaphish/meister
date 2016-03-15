#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run the meister."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import os
import time

import meister.settings

import meister.cgc.ticlient
from meister.creators.afl import AFLCreator
from meister.creators.rex import RexCreator
from meister.creators.driller import DrillerCreator
from meister.creators.patcherex import PatcherexCreator
from meister.schedulers.brute import BruteScheduler


def main():
    """Run the meister."""
    # Initialize APIs
    cgc = meister.cgc.ticlient.TiClient.from_env()
    while not cgc.ready():
        time.sleep(5)

    # Scheduler strategy
    scheduler = BruteScheduler(cgc=cgc, creators=[
        AFLCreator(cgc),
        DrillerCreator(cgc),
        RexCreator(cgc),
        PatcherexCreator(cgc),
    ])
    scheduler.run()

if __name__ == '__main__':
    main()
