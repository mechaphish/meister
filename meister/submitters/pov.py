#!/usr/bin/env python

from farnsworth.models import ChallengeSet, Team
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('povsubmitter')

class POVSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc

    def run(self):
        for team in Team.opponents():
            for cs in ChallengeSet.fielded_in_round():
                for exploit in cs.unsubmitted_exploits:
                    LOG.info("Submitting POV for %s to team %s", cs.name, team.name)
                    throws = 10
                    try:
                        result = self._cgc.uploadPOV(str(cs.name),
                                                     str(team.name),
                                                     str(throws),
                                                     str(exploit.blob))
                        exploit.submit_to(teams=team.name, throws=throws)
                        LOG.debug("Submitted POV! Response: %s", result)
                        break
                    except TiError as e:
                        LOG.error("Submission POV error: %s", e.message)
