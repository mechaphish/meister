#!/usr/bin/env python

from farnsworth import ChallengeBinaryNode
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('cbsubmitter')

class CBSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc

    def run(self):
        LOG.debug("Submitting patched binaries")
        for cbn in ChallengeBinaryNode.unsubmitted_patched():
            try:
                self._cgc.uploadRCB(str(cbn.cs_id),
                                    (str(cbn.parent.name), str(cbn.blob)))
                cbn.submitted()
                return          # FIXME: we submit only one patch per round
            except TiError as e:
                LOG.error("Submission error: %s", e.message)
