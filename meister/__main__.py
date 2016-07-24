#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Run the meister."""

from __future__ import absolute_import, unicode_literals

import sys
import time

# leave this import before everything else!
import meister.settings

from farnsworth.models import Round

from meister.brains.elephant import ElephantBrain
from meister.creators.afl import AFLCreator
from meister.creators.backdoor import BackdoorSubmitterCreator
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
from meister.creators.pov_tester import PovTesterCreator
from meister.creators.rex import RexCreator
from meister.creators.rop_cache import RopCacheCreator
from meister.creators.showmap_sync import ShowmapSyncCreator
import meister.log
from meister.schedulers.priority import PriorityScheduler
from meister.submitters.cb import CBSubmitter
from meister.submitters.pov import POVSubmitter

LOG = meister.log.LOG.getChild('main')


def wait_for_ambassador():
    POLL_INTERVAL = 3
    while not (Round.current_round() and Round.current_round().is_ready()):
        LOG.info("Round data not available, waiting %d seconds", POLL_INTERVAL)
        time.sleep(POLL_INTERVAL)


def main(args=[]):
    """Run the meister."""
    brain = ElephantBrain()
    submitters = [POVSubmitter(), CBSubmitter()]
    creators = [DrillerCreator(),
                RexCreator(),
                PovFuzzer1Creator(),
                PovFuzzer2Creator(),
                ColorGuardCreator(),
                AFLCreator(),
                BackdoorSubmitterCreator(),
                CacheCreator(),
                RopCacheCreator(),
                PatcherexCreator(),
                # IDSCreator(),
                FunctionIdentifierCreator(),
                NetworkPollCreatorCreator(),
                ShowmapSyncCreator(),
                PatchPerformanceCreator(),
                # VM jobs
                PollCreatorCreator(),
                NetworkPollSanitizerCreator(),
                CBTesterCreator(),
                PovTesterCreator()]

    scheduler = PriorityScheduler(brain, creators)

    while True:
        wait_for_ambassador()

        LOG.info("Round #%d", Round.current_round().num)

        scheduler.run()

        for submitter in submitters:
            submitter.run(Round.current_round().num)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
