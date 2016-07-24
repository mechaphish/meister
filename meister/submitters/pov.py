#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models.challenge_set import ChallengeSet
from farnsworth.models.challenge_set_fielding import ChallengeSetFielding
from farnsworth.models.exploit_submission_cable import ExploitSubmissionCable
from farnsworth.models.ids_rule_fielding import IDSRuleFielding
from farnsworth.models.pov_test_result import PovTestResult
from farnsworth.models.team import Team

import meister.submitters

LOG = meister.submitters.LOG.getChild('pov')


class POVSubmitter(object):

    def run(self, current_round=None, random_submit=False):
        for team in Team.opponents():
            throws = 10
            for cs in ChallengeSet.fielded_in_round():
                cs_fieldings = ChallengeSetFielding.latest(cs, team)
                ids_fieldings = IDSRuleFielding.latest(cs, team)
                to_submit_pov = None

                if cs_fieldings:
                    target_cs_fielding = cs_fieldings[0]
                    target_ids_fielding = ids_fieldings[0] if ids_fieldings else None

                    # See, if there are any results against current cs_fielding and ids_fielding.
                    results = PovTestResult.best(target_cs_fielding, target_ids_fielding)
                    if not results:
                        # Ignore IDS and see, if we have a Tested PoV against the cs fielding.
                        results = PovTestResult.best_for_cs(target_cs_fielding)

                    if not results:
                        # OK, we do not have any PoVs tested against the current cs fielding.
                        # Get the PoV, most successful against current CS.
                        results = PovTestResult.best_against_cs(target_cs_fielding.cs)

                    if results:
                        # Good, we have a PovTestResult to submit.
                        # FIXME: Should we take the most reliable against this CS and IDS?
                        to_submit_pov = results[0].exploit
                        LOG.info("Submitting a tested PoV %s against team=%s cs=%s",
                                 to_submit_pov.id, team.name, cs.name)

                else:
                    # No, latest CS fielding, something wrong!!
                    LOG.warn("No CS fielding available for team=%s cs=%s", team.name, cs.name)

                # We do not have a specific PoV, hence submit the most reliable PoV we have
                if to_submit_pov is None and cs.exploits:
                    to_submit_pov = cs.most_reliable_exploit
                    LOG.info("Submitting most reliable POV %s against team=%s cs=%s",
                                to_submit_pov.id, team.name, cs.name)

                # Submit our PoV
                if to_submit_pov is not None:
                    # Do not resubmit an exploit for a given team if it is currently active
                    if ExploitSubmissionCable.most_recent_for_team(team, cs) != to_submit_pov:
                        ExploitSubmissionCable.create(team=team,
                                                      cs=cs,
                                                      exploit=to_submit_pov,
                                                      throws=throws)
                        LOG.debug("POV %s marked for submission", to_submit_pov.id)
                else:
                    LOG.warn("No POV to submit for team=%s cs=%s", team.name, cs.name)
