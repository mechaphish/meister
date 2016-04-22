#!/usr/bin/env python

from farnsworth.models import ChallengeBinaryNode, Team
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('povsubmitter')

class POVSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc

    def run(self):
        for team in Team.opponents():
            for cbn in ChallengeBinaryNode.roots():
                for exploit in cbn.unsubmitted_exploits:
                    LOG.debug("Submitting POV for %s to team %s", cbn.name, team.name)
                    try:
                        result = self._cgc.uploadPOV(str(cbn.cs_id),
                                                     str(team.name),
                                                     "10",
                                                     str(exploit.blob))
                        exploit.submitted_to(teams=team.name)
                        LOG.debug("Submitted POV! Response: %s", result)
                        break
                    except TiError as e:
                        LOG.error("Submission POV error: %s", e.message)
