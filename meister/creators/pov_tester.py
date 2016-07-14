#!/usr/bin/env/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import PovTesterJob
from farnsworth.models import Team, ChallengeSetFielding, IDSRuleFielding, PovTestResult, Exploit

import meister.creators
LOG = meister.creators.LOG.getChild('pov_tester')


class PovTesterCreator(meister.creators.BaseCreator):

    # Number of times the PoV has to be passed to be considered successful against a team.
    SUCCESS_THRESHOLD = 4

    @staticmethod
    def _get_best_pov_test_results(cs_fielding, ids_fielding):
        """
            Get best PoV test results for the provided cs fielding and ids fielding.

        :param cs_fielding: CS fielding for which PoVTestResult need to be fetched.
        :param ids_fielding: IDS fielding for which PoVTestResult need to be fetched.
        :return: List containing best PoV test result.
        """
        condition = PovTestResult.cs_fielding.sha256 == cs_fielding.sha256
        if ids_fielding is None:
            condition &= PovTestResult.ids_fielding.is_null(True)
        else:
            condition &= PovTestResult.ids_fielding.sha256 == ids_fielding.sha256
        return PovTestResult.select().where(condition).order_by(PovTestResult.num_success.desc()).limit(1)

    @staticmethod
    def _get_exploit_test_results(target_exploit, cs_fielding, ids_fielding):
        """
            Get results for the provided exploit on cs_fielding and ids_fielding
        :param cs_fielding: CS fielding for which PoV testing results need to be fetched.
        :param ids_fielding: IDS fielding for which PoV testing results need to be fetched.
        :return: List of PoVTestResult objects
        """
        condition = (PovTestResult.exploit == target_exploit) & (PovTestResult.cs_fielding.sha256 == cs_fielding.sha256)
        if ids_fielding is None:
            condition &= PovTestResult.ids_fielding.is_null(True)
        else:
            condition &= PovTestResult.ids_fielding.sha256 == ids_fielding.sha256
        return PovTestResult.select().where(condition)

    @staticmethod
    def _get_latest_cs_fielding(target_team, target_cs):
        """
            Get latest cs fielding for provided team and CS
        :param target_team: Team for which cs fielding need to be fetched.
        :param target_cs: CS for which fielding need to be fetched.
        :return: list containing latest cs fielding.
        """
        curr_cs_fieldings = ChallengeSetFielding.select().where(ChallengeSetFielding.team == target_team & ChallengeSetFielding.cs == target_cs).\
            order_by(ChallengeSetFielding.submission_round.num.desc()).limit(1)
        return curr_cs_fieldings

    @staticmethod
    def _get_latest_ids_fielding(target_team, target_cs):
        """
            Get latest IDS fielding for provided team and CS.
        :param target_team: Team for which IDS fielding need to be fetched.
        :param target_cs: CS for which IDS fielding need to be fetched.
        :return: list containing latest IDS fielding.
        """
        curr_ids_fieldings = IDSRuleFielding.select().where(IDSRuleFielding.team == target_team & IDSRuleFielding.ids_rule.cs == target_cs).\
            order_by(IDSRuleFielding.submission_round.num.desc()).limit(1)
        return curr_ids_fieldings

    @property
    def jobs(self):
        for curr_team in Team.opponents():
            # TODO: only currently active CS
            # Is this correct?
            for curr_cs in ChallengeSetFielding.all():
                # Get Latest submitted CS
                curr_cs_fieldings = PovTesterCreator._get_latest_cs_fielding(curr_team, curr_cs)
                # if there is any CS fielded?
                if len(curr_cs_fieldings) > 0:
                    target_cs_fld = curr_cs_fieldings[0]
                    target_ids_fld = None
                    # get Latest ids fielded for that team and CS
                    curr_ids_fieldings = PovTesterCreator._get_latest_ids_fielding(curr_team, curr_cs)
                    if len(curr_ids_fieldings) > 0:
                        target_ids_fld = curr_ids_fieldings[0]
                    # see if there are successful PoVs for this fielded CS and IDS.
                    # if yes, no need to schedule Pov Testing Jobs
                    pov_test_results = PovTesterCreator._get_best_pov_test_results(target_cs_fld, target_ids_fld)
                    # no results or we do not have strong PoV's?
                    if len(pov_test_results) == 0 or pov_test_results[0].num_success >= PovTesterCreator.SUCCESS_THRESHOLD:
                        # OK, we do not have any successful PoVs for the current fielded CS.
                        # schedule jobs for all PoVs, if they are not tested before.
                        for curr_exploit in Exploit.select().where(Exploit.cbn.cs == target_cs_fld.cs):
                            # if this exploit is not tested, then schedule the PovTesterJob
                            available_test_results = PovTesterCreator.\
                                _get_exploit_test_results(curr_exploit, target_cs_fld, target_ids_fld)
                            if len(available_test_results) == 0:
                                # Schedule a Pov Tester Job for this
                                job_payload = {'exploit_id': curr_exploit.id, 'cs_fld_hash' : target_cs_fld.sha256}
                                if target_ids_fld is not None:
                                    job_payload['ids_fld_hash'] = target_ids_fld.sha256
                                target_job = PovTesterJob.get_or_create(cs=curr_cs, payload=job_payload)
                                # Set priority
                                target_job.priority = 100
                                yield target_job
                            else:
                                LOG.info("Ignoring Exploit %s for Team %s For CS %s as it is already tested",
                                         curr_exploit.id, curr_team.name, curr_cs.name)
                    else:
                        LOG.info("Successful PoV already exists for Team %s For CS %s, no PoV Tester Jobs scheduled",
                                 curr_team.name, curr_cs.name)

                else:
                    LOG.warn("No CS fielding exist for Team %s For CS %s, no PoV Tester Jobs scheduled",
                             curr_team.name, curr_cs.name)
