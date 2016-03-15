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
from meister.submitters.cb import CBSubmitter
import meister.log

LOG = meister.log.LOG.getChild('main')

def main():
    """Run the meister."""
    # Initialize APIs
    cgc = meister.cgc.ticlient.TiClient.from_env()
    while not cgc.ready():
        time.sleep(5)

    previous_round = None
    while True:
        current_round = cgc.getRound()
        if current_round == previous_round:
            LOG.debug("Still round #%d, waiting", current_round)
            time.sleep(3)
            continue
        else:
            LOG.info("Round #%d", current_round)
            previous_round = cgc.getRound()

        # Scheduler strategy
        scheduler = BruteScheduler(cgc=cgc, creators=[
            AFLCreator(cgc),
            DrillerCreator(cgc),
            RexCreator(cgc),
            PatcherexCreator(cgc),
        ])
        scheduler.run()

        # Submit patched binaries
        CBSubmitter(cgc).run()
        # POVSubmitter(cgc).run()

        # Get feedbacks
        # CBFeedback(cgc).run()
        # POVFeedback(cgc).run()


if __name__ == '__main__':
    main()
