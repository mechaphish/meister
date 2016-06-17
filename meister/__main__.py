#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run the meister."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import os
import time

import meister.settings

import meister.cgc.ticlient
import meister.cgc.tierror
from meister.creators.afl import AFLCreator
from meister.creators.driller import DrillerCreator
from meister.creators.ids import IDSCreator
from meister.creators.patcherex import PatcherexCreator
from meister.creators.rex import RexCreator
from meister.creators.tester import TesterCreator
from meister.creators.wererabbit import WereRabbitCreator
from meister.schedulers.brute import BruteScheduler
from meister.submitters.cb import CBSubmitter
from meister.submitters.ids import IDSSubmitter
from meister.submitters.pov import POVSubmitter
from meister.evaluators import Evaluator
from meister.notifier import Notifier
from farnsworth.models import Round
import meister.log

LOG = meister.log.LOG.getChild('main')

def main():
    """Run the meister."""
    # Initialize APIs
    cgc = meister.cgc.ticlient.TiClient.from_env()

    previous_round = None
    notifier = Notifier()
    while True:
        try:
            # wait for API to be available
            while not cgc.ready():
                notifier.api_is_down()
                time.sleep(5)

            notifier.api_is_up()
            current_round = cgc.getRound()
            round_ = Round.find_or_create(num = current_round)

            # Jobs scheduled continuously
            scheduler = BruteScheduler(cgc=cgc, creators=[
                DrillerCreator(cgc),
                RexCreator(cgc),
                ColorGuardCreator(cgc),
                TesterCreator(cgc),
                WereRabbitCreator(cgc),
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
                IDSCreator(cgc),
            ])
            perround_scheduler.run()

            # Submit! Order matters!
            CBSubmitter(cgc).run(current_round, random_submit=True)
            # IDSSubmitter(cgc).run(current_round)
            POVSubmitter(cgc).run()

        except meister.cgc.tierror.TiError:
            notifier.api_is_down()

if __name__ == '__main__':
    main()
