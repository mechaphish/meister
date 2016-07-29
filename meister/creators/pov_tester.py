#!/usr/bin/env/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models.challenge_set_fielding import ChallengeSetFielding
from farnsworth.models.ids_rule_fielding import IDSRuleFielding
from farnsworth.models.job import PovTesterJob
from farnsworth.models.pov_test_result import PovTestResult
from farnsworth.models.team import Team
from farnsworth.models.exploit import Exploit

import meister.creators

LOG = meister.creators.LOG.getChild('pov_tester')


class PovTesterCreator(meister.creators.BaseCreator):

    # Number of times the PoV has to be passed to be considered successful against a team.
    SUCCESS_THRESHOLD = 4

    @property
    def _jobs(self):
        for team in Team.opponents():
            for cs in self.challenge_sets():
                target_cs_fld = ChallengeSetFielding.latest(cs, team)

                # if there is any CS fielded?
                if target_cs_fld is not None:
                    target_ids_fld = IDSRuleFielding.latest(cs, team)

                    # see if there are successful PoVs for this fielded CS and IDS.
                    # if yes, no need to schedule Pov Testing Jobs
                    pov_test_results = PovTestResult.best(target_cs_fld, target_ids_fld)

                    # no results or we do not have strong PoV's?
                    if pov_test_results is None or \
                            pov_test_results.num_success < self.SUCCESS_THRESHOLD:

                        # OK, we do not have any successful PoVs for the current fielded CS.
                        # schedule jobs for all PoVs, if they are not tested before.
                        for exploit in target_cs_fld.cs.exploits.select(Exploit.id):
                            # if this exploit is not tested, then schedule the PovTesterJob
                            results = PovTestResult.best_exploit_test_results(exploit,
                                                                              target_cs_fld,
                                                                              target_ids_fld)

                            if results is None:
                                # Schedule a Pov Tester Job for this
                                job_payload = {'exploit_id': exploit.id,
                                               'cs_fld_hash': target_cs_fld.sha256}

                                if target_ids_fld is not None:
                                    job_payload['ids_fld_hash'] = target_ids_fld.sha256

                                job = PovTesterJob(cs=cs, payload=job_payload,
                                                   request_cpu=4, request_memory=4096*2)

                                LOG.info("Yielding PovTesterJob for exploit %s", str(exploit.id))
                                yield (job, 100)

                            else:
                                LOG.info("Ignoring exploit=%s team=%s cs=%s as it is already tested",
                                         exploit.id, team.name, cs.name)
                    else:
                        LOG.info("Successful PoV already exists team=%s cs=%s, no jobs scheduled",
                                 team.name, cs.name)
                else:
                    LOG.warn("No CS fieldings with team=%s cs=%s, no jobs scheduled",
                             team.name, cs.name)
