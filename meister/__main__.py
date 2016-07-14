#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run the meister."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import sys
import time

# leave this import before everything else!
import meister.settings

from farnsworth.models import Round

import meister.cgc.ticlient
import meister.cgc.tierror
from meister.creators.afl import AFLCreator
from meister.creators.cache import CacheCreator
from meister.creators.cb_tester import CBTesterCreator
from meister.creators.colorguard import ColorGuardCreator
from meister.creators.driller import DrillerCreator
from meister.creators.ids import IDSCreator
from meister.creators.function_identifier import FunctionIdentifierCreator
from meister.creators.patcherex import PatcherexCreator
from meister.creators.poll_creator import PollCreatorCreator
from meister.creators.network_poll_creator import NetworkPollCreatorCreator
from meister.creators.network_poll_sanitizer import NetworkPollSanitizerCreator
from meister.creators.rex import RexCreator
from meister.creators.povfuzzer1 import PovFuzzer1Creator
from meister.creators.povfuzzer2 import PovFuzzer2Creator
from meister.creators.tester import TesterCreator
from meister.creators.were_rabbit import WereRabbitCreator
from meister.evaluators import Evaluator
from meister.notifier import Notifier
import meister.log
from meister.schedulers.priority import PriorityScheduler
from meister.submitters.cb import CBSubmitter
from meister.submitters.pov import POVSubmitter

LOG = meister.log.LOG.getChild('main')


def main(args=None):
    """Run the meister."""
    if args is None:
        args = []
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
            round_, _ = Round.get_or_create(num=current_round)

            # Jobs scheduled continuously
            scheduler = PriorityScheduler(cgc=cgc, creators=[
                DrillerCreator(cgc),
                RexCreator(cgc),
                PovFuzzer1Creator(cgc),
                PovFuzzer2Creator(cgc),
                ColorGuardCreator(cgc),
                CbTesterCreator(cgc),
                WereRabbitCreator(cgc),
                AFLCreator(cgc),
                CacheCreator(cgc),
                PatcherexCreator(cgc),
                IDSCreator(cgc),
                FunctionIdentifierCreator(cgc),
                NetworkPollCreatorCreator(cgc),
                # VM jobs
                PollCreatorCreator(cgc),
                # # VM jobs
                NetworkPollSanitizerCreator(cgc),
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

            # Submit! Order matters!
            CBSubmitter(cgc).run(current_round, random_submit=True)
            POVSubmitter(cgc).run()

        except meister.cgc.tierror.TiError:
            notifier.api_is_down()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
