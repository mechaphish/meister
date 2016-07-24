#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import ChallengeSet, ExploitSubmissionCable, Team

from ..helpers.pov_test import PovTestHelper
import meister.submitters

LOG = meister.submitters.LOG.getChild('pov')


class POVSubmitter(object):

    def run(self, current_round=None, random_submit=False):
        for team in Team.opponents():
            throws = 10
            for cs in ChallengeSet.fielded_in_round():
                # Get the fielded CS and fielded IDS
                latest_cs_fieldings = PovTestHelper.get_latest_cs_fielding(team, cs)
                latest_ids_fieldings = PovTestHelper.get_latest_ids_fielding(team, cs)
                to_submit_pov = None
                if len(latest_cs_fieldings) > 0:
                    target_cs_fielding = latest_cs_fieldings[0]
                    target_ids_fielding = None
                    if len(latest_ids_fieldings) > 0:
                        target_ids_fielding = latest_ids_fieldings[0]
                    # See, if there are any results against current cs_fielding and ids_fielding.
                    available_results = PovTestHelper.get_best_pov_test_results(target_cs_fielding, target_ids_fielding)
                    if len(available_results) <= 0:
                        # Ignore IDS and see, if we have a Tested PoV against the cs fielding.
                        available_results = PovTestHelper.get_best_pov_cs_results(target_cs_fielding)
                    if len(available_results) <= 0:
                        # OK, we do not have any PoVs tested against the current cs fielding.
                        # Get the PoV, most successful against current CS.
                        available_results = PovTestHelper.get_best_pov_against_cs(target_cs_fielding.cs)
                    if len(available_results) > 0:
                        # Good, we have a PovTestResult to submit.
                        to_submit_pov = available_results[0].exploit
                        LOG.info("Submitting a Tested PoV %s against team %s for CS %s",
                                 to_submit_pov.id, team.name, cs.name)

                else:
                    # No, latest CS fielding, something wrong!!
                    LOG.warn("No CS fielding available for Team %s for CS %s", team.name, cs.name)

                if to_submit_pov is None:
                    # OK, we do not have any PoVs tested against current CS.
                    # Get any exploit for the current CS and submit it.
                    available_povs = cs.exploits
                    if len(available_povs) > 0:
                        # OK, we select a random PoV from available PoVs and submit.
                        most_reliable = cs.most_reliable_exploit
                        if most_reliable.reliability > 0:
                            to_submit_pov = most_reliable
                            LOG.info("Submitting most reliable POV %s against team %s for CS %s",
                                     to_submit_pov.id, team.name, cs.name)

                if to_submit_pov is not None:

                    # if the most recent exploit submission for a given team has the same exploit id
                    # do not resubmit

                    if ExploitSubmissionCable.most_recent_for_team(team, cs) != to_submit_pov:
                        ExploitSubmissionCable.create(team=team,
                                                      cs=cs,
                                                      exploit=to_submit_pov,
                                                      throws=throws)
                        LOG.debug("POV %s marked for submission", to_submit_pov.id)
                else:
                    LOG.warn("No PoV to submit for Team %s for CS %s", team.name, cs.name)
