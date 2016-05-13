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
from meister.creators.tester import TesterCreator
from meister.schedulers.brute import BruteScheduler
from meister.submitters.cb import CBSubmitter
from meister.submitters.pov import POVSubmitter
from meister.evaluators import Evaluator
from farnsworth.models import Round
import meister.log

LOG = meister.log.LOG.getChild('main')

def main():
    """Run the meister."""
    # Initialize APIs
    cgc = meister.cgc.ticlient.TiClient.from_env()

    previous_round = None
    while True:
        # wait for API to be available
        while not cgc.ready():
            time.sleep(5)

        current_round = cgc.getRound()
        round_ = Round.find_or_create(current_round)

        # Jobs scheduled continuously
        scheduler = BruteScheduler(cgc=cgc, creators=[
            DrillerCreator(cgc),
            RexCreator(cgc),
            TesterCreator(cgc),
        ])
        scheduler.run()

        # Get feedbacks
        Evaluator(cgc, round_).run()

        if current_round == previous_round:
            LOG.debug("Still round #%d, waiting", current_round)
            time.sleep(1)
            continue
        else:
            LOG.info("Round #%d", current_round)
            previous_round = current_round

        # Jobs scheduled per round
        perround_scheduler = BruteScheduler(cgc=cgc, creators=[
            AFLCreator(cgc),
            PatcherexCreator(cgc),
        ])
        perround_scheduler.run()

        # Submit patched binaries every 2 rounds
        # CBSubmitter(cgc).run()
        POVSubmitter(cgc).run()


if __name__ == '__main__':
    main()
