#!/usr/bin/env python

from farnsworth import ChallengeBinaryNode
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('cbsubmitter')

class CBSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc

    def run(self):
        for cbn in ChallengeBinaryNode.roots():
            for patch in cbn.unsubmitted_patches:
                LOG.debug("Submitting patch %s for %s", patch.name, cbn.name)
                try:
                    self._cgc.uploadRCB(str(cbn.cs_id),
                                        (str(cbn.name), str(patch.blob)))
                    patch.submitted()
                    break          # FIXME: we submit only one patch per round
                except TiError as e:
                    LOG.error("Submission error: %s", e.message)
