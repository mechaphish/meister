#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run the meister."""

from __future__ import absolute_import, unicode_literals

import sys
import time

# leave this import before everything else!
import meister.settings

from farnsworth.models import Round

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
from meister.creators.patch_performance import PatchPerformanceCreator
from meister.creators.povfuzzer1 import PovFuzzer1Creator
from meister.creators.povfuzzer2 import PovFuzzer2Creator
from meister.creators.rex import RexCreator
from meister.creators.rop_cache import RopCacheCreator
from meister.creators.pov_tester import PovTesterCreator
import meister.log
from meister.schedulers.priority import PriorityScheduler
from meister.submitters.cb import CBSubmitter
from meister.submitters.pov import POVSubmitter

LOG = meister.log.LOG.getChild('main')


def wait_for_ambassador():
    POLL_INTERVAL = 3
    while Round.current_round() is None:
        LOG.info("Game not started, waiting %d seconds", POLL_INTERVAL)
        time.sleep(POLL_INTERVAL)


def main(args=[]):
    """Run the meister."""
    cbsubmitter = CBSubmitter()
    while True:
        wait_for_ambassador()

        LOG.info("Round #%d", Round.current_round().num)

        scheduler = PriorityScheduler(creators=[
            DrillerCreator(),
            RexCreator(),
            PovFuzzer1Creator(),
            PovFuzzer2Creator(),
            ColorGuardCreator(),
            AFLCreator(),
            CacheCreator(),
            RopCacheCreator(),
            PatcherexCreator(),
            # IDSCreator(),
            FunctionIdentifierCreator(),
            NetworkPollCreatorCreator(),
            # PatchPerformanceCreator(),
            # VM jobs
            # PollCreatorCreator(),
            # NetworkPollSanitizerCreator(),
            # CBTesterCreator(),
            # PovTesterCreator()
        ])
        scheduler.run()

        # Submit!
        cbsubmitter.run(Round.current_round().num)
        POVSubmitter().run()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
