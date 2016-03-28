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
from meister.evaluators import Evaluator
from farnsworth import Round
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
        round_ = Round.find_or_create(current_round)

        # Get feedbacks
        # FIXME: 5-minutes horrible code
        Evaluator(cgc, round_).run()

        if current_round == previous_round:
            LOG.debug("Still round #%d, waiting", current_round)
            time.sleep(1)
            continue
        else:
            LOG.info("Round #%d", current_round)
            previous_round = current_round

        # Scheduler strategy
        scheduler = BruteScheduler(cgc=cgc, creators=[
            AFLCreator(cgc),
            DrillerCreator(cgc),
            RexCreator(cgc),
            PatcherexCreator(cgc),
        ])
        scheduler.run()

        # Submit patched binaries every 2 rounds
        CBSubmitter(cgc).run()
        # POVSubmitter(cgc).run()


if __name__ == '__main__':
    main()
