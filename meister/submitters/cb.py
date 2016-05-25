#!/usr/bin/env python

import random
from farnsworth.models import ChallengeBinaryNode, IDSRule
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('cbsubmitter')

class CBSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc

    def run(self, current_round, random_submit=False):
        # submit only in odd rounds, see FAQ163 & FAQ157
        if (current_round % 2) == 1:
            for cbn in ChallengeBinaryNode.roots():
                submitted_ids = cbn.cs.ids_rules.where(IDSRule.submitted_at.is_null(True))
                # dont' submit CB that has IDS active
                if len(submitted_ids) > 0:
                    continue
                # submit patches for 50% of binaries, so we can test IDs on the other 50%
                if random_submit and (random.randint(0,1) == 0):
                    continue

                for patch in cbn.unsubmitted_patches:
                    LOG.info("Submitting patch %s for %s on round %s",
                             patch.name, cbn.name, current_round)
                    try:
                        self._cgc.uploadRCB(str(cbn.cs.name),
                                            (str(cbn.name), str(patch.blob)))
                        patch.submit()
                        # FIXME: we submit only one patch type at once
                        break
                    except TiError as e:
                        LOG.error("Submission error: %s", e.message)
