#!/usr/bin/env/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import PovTesterJob
from farnsworth.models import Team, ChallengeSetFielding, IDSRuleFielding, PovTestResult, Exploit

import meister.creators
LOG = meister.creators.LOG.getChild('pov_tester')


class PovTesterCreator(meister.creators.BaseCreator):
    SUCCESS_THRESHOLD = 4
    @property
    def jobs(self):
        for curr_team in Team.opponents():
            # TODO: only currently active CS
            for curr_cs in ChallengeSetFielding.all():
                # Get Latest submitted CS
                curr_cs_fieldings = ChallengeSetFielding.select().where(ChallengeSetFielding.team == curr_team & ChallengeSetFielding.cs == curr_cs).\
                    order_by(ChallengeSetFielding.submission_round.num.desc()).limit(1)
                # if there is any CS fielded?
                if len(curr_cs_fieldings) > 0:
                    target_cs_fld = curr_cs_fieldings[0]
                    target_ids_fld = None
                    # get any ids fielded for that team.
                    curr_ids_fieldings = IDSRuleFielding.select().where(IDSRuleFielding.team == curr_team & IDSRuleFielding.ids_rule.cs == curr_cs).\
                        order_by(IDSRuleFielding.submission_round.num.desc()).limit(1)
                    if len(curr_ids_fieldings) > 0:
                        target_ids_fld = curr_ids_fieldings[0]
                    # see if there are successful PoVs for this fielded CS and IDS.
                    # if yes, no need to schedule Pov Testing Jobs
                    if target_ids_fld is None:
                        pov_test_results = PovTestResult.select().\
                            where(PovTestResult.cs_fielding.sha256 == target_cs_fld.sha256 & PovTestResult.ids_fielding == None).order_by(PovTestResult.num_success.desc()).limit(1)
                    else:
                        pov_test_results = PovTestResult.select().\
                            where(PovTestResult.cs_fielding.sha256 == target_cs_fld.sha256 & PovTestResult.ids_fielding.sha256 == target_ids_fld.sha256).order_by(PovTestResult.num_success.desc()).limit(1)
                    # no results or we do not have strong PoV's?
                    if len(pov_test_results) == 0 or pov_test_results[0].num_success >= PovTesterCreator.SUCCESS_THRESHOLD:
                        # OK, we do not have any successful PoVs for the current fielded CS.
                        # schedule jobs for all PoVs, if they are not tested before.
                        for curr_exploit in Exploit.select().where(Exploit.cbn.cs == target_cs_fld.cs):
                            # if this exploit is not tested, then schedule the PovTesterJob
                            if target_ids_fld is None:
                                available_test_results = PovTestResult.select().\
                                    where(PovTestResult.exploit == curr_exploit & PovTestResult.cs_fielding.sha256 == target_cs_fld.sha256)
                            else:
                                available_test_results = PovTestResult.select().\
                                    where(PovTestResult.exploit == curr_exploit & PovTestResult.cs_fielding.sha256 == target_cs_fld.sha256 & PovTestResult.ids_fielding.sha256 == target_ids_fld.sha256)
                            if len(available_test_results) == 0:
                                # Schedule a Pov Tester Job for this
                                job_payload = {'exploit_id' : curr_exploit.id, 'cs_fld_hash' : target_cs_fld.sha256}
                                if target_ids_fld is not None:
                                    job_payload['ids_fld_hash'] = target_ids_fld.sha256
                                target_job = PovTesterJob.get_or_create(cs=curr_cs, payload=job_payload)
                                # Set priority
                                target_job.priority = 100
                                yield target_job
                            else:
                                # TODO: log
                                pass
                    else:
                        # TODO: log
                        pass

            else:
                # TODO: log
                pass
