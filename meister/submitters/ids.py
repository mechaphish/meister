#!/usr/bin/env python

from farnsworth.models import ChallengeSet, IDSRule
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('idssubmitter')

# FIXME: remove
class IDSSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc

    def run(self, current_round):
        # submit only in odd rounds, see FAQ163 & FAQ157
        if (current_round % 2) == 1:
            for cs in ChallengeSet.all():
                submitted_patches = [True for cbn in cs.cbns
                                     if len(cbn.submitted_patches) > 0]

                # dont' submit IDS for patched binaries
                if len(submitted_patches) > 0:
                    continue

                for ids in cs.unsubmitted_ids_rules:
                    LOG.info("Submitting IDS rule for %s on round %s",
                             cs.name, current_round)
                    try:
                        self._cgc.uploadIDS(str(cs.name), str(ids.rules))
                        ids.submit()
                        # FIXME: we submit only one IDS rule per round
                        break
                    except TiError as e:
                        LOG.error("Submission error: %s", e.message)
