#!/usr/bin/env python

from farnsworth.models import ChallengeBinaryNode
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('cbsubmitter')

class CBSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc

    def run(self, current_round):
        # submit only in odd rounds, see FAQ163 & FAQ157
        if (current_round % 2) == 1:
            for cbn in ChallengeBinaryNode.roots():
                for patch in cbn.unsubmitted_patches:
                    LOG.debug("Submitting patch %s for %s on round %s",
                              patch.name, cbn.name, current_round)
                    try:
                        self._cgc.uploadRCB(str(cbn.cs_id),
                                            (str(cbn.name), str(patch.blob)))
                        patch.submit()
                        # FIXME: we submit only one patch type at once
                        break
                    except TiError as e:
                        LOG.error("Submission error: %s", e.message)
