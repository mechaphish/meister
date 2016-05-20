#!/usr/bin/env python

from farnsworth.models import ChallengeSet, IDSRule
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('idssubmitter')

class IDSSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc

    def run(self, current_round):
        # submit only in odd rounds, see FAQ163 & FAQ157
        if (current_round % 2) == 1:
            for cs in ChallengeSet.all():
                for ids in cs.unsubmitted_ids_rules:
                    LOG.debug("Submitting IDS rule for %s on round %s",
                              cs.name, current_round)
                    try:
                        self._cgc.uploadIDS(str(cs.name), str(ids.rules))
                        ids.submit()
                        # FIXME: we submit only one IDS rule per round
                        break
                    except TiError as e:
                        LOG.error("Submission error: %s", e.message)
