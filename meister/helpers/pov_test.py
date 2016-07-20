#!/usr/bin/env/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import ChallengeSetFielding, IDSRuleFielding, PovTestResult, Round, IDSRule, Exploit


class PovTestHelper(object):

    @staticmethod
    def get_best_pov_test_results(cs_fielding, ids_fielding):
        """
            Get best PoV test results for the provided cs fielding and ids fielding.

        :param cs_fielding: CS fielding for which PoVTestResult need to be fetched.
        :param ids_fielding: IDS fielding for which PoVTestResult need to be fetched.
        :return: List containing best PoV test result.
        """
        query = PovTestResult.select(PovTestResult).join(ChallengeSetFielding)
        predicate = ChallengeSetFielding.sha256 == cs_fielding.sha256

        if ids_fielding is None:
            predicate &= PovTestResult.ids_fielding.is_null(True)
        else:
            predicate &= IDSRuleFielding.sha256 == ids_fielding.sha256
            query = query.join(IDSRuleFielding, on=(IDSRuleFielding.id == PovTestResult.ids_fielding))

        return query.where(predicate).order_by(PovTestResult.num_success.desc()).limit(1)

    @staticmethod
    def get_best_pov_cs_results(cs_fielding):
        """
            Get best PoV test results for the provided cs fielding.

        :param cs_fielding: CS fielding for which PoVTestResult need to be fetched.
        :return: List containing best PoV test result.
        """
        query = PovTestResult.select(PovTestResult).join(ChallengeSetFielding)
        predicate = ChallengeSetFielding.sha256 == cs_fielding.sha256
        return query.where(predicate).order_by(PovTestResult.num_success.desc()).limit(1)

    @staticmethod
    def get_best_pov_against_cs(target_cs):
        """
            Get best PoV test results for the provided cs .

        :param target_cs: CS for which best PoVTestResult need to be fetched.
        :return: List containing best PoV test result.
        """
        query = PovTestResult.select(PovTestResult).join(ChallengeSetFielding)
        predicate = ChallengeSetFielding.cs == target_cs
        return query.where(predicate).order_by(PovTestResult.num_success.desc()).limit(1)

    @staticmethod
    def get_exploit_test_results(target_exploit, cs_fielding, ids_fielding):
        """
            Get results for the provided exploit on cs_fielding and ids_fielding
        :param target_exploit: Exploit for which results needs to be fetched.
        :param cs_fielding: CS fielding for which PoV testing results need to be fetched.
        :param ids_fielding: IDS fielding for which PoV testing results need to be fetched.
        :return: List of PoVTestResult objects
        """
        query = PovTestResult.select(PovTestResult).join(ChallengeSetFielding)
        predicate = (ChallengeSetFielding.sha256 == cs_fielding.sha256) & (PovTestResult.exploit == target_exploit)

        if ids_fielding is None:
            predicate &= PovTestResult.ids_fielding.is_null(True)
        else:
            predicate &= IDSRuleFielding.sha256 == ids_fielding.sha256
            query = query.join(IDSRuleFielding, on=(IDSRuleFielding.id == PovTestResult.ids_fielding))

        return query.where(predicate).order_by(PovTestResult.num_success.desc())

    @staticmethod
    def get_latest_cs_fielding(target_team, target_cs):
        """
            Get latest cs fielding for provided team and CS
        :param target_team: Team for which cs fielding need to be fetched.
        :param target_cs: CS for which fielding need to be fetched.
        :return: list containing latest cs fielding.
        """

        query = ChallengeSetFielding.select().join(Round, on=(ChallengeSetFielding.available_round == Round.id))
        predicate = (ChallengeSetFielding.team == target_team) & (ChallengeSetFielding.cs == target_cs)
        return query.where(predicate).order_by(Round.num.desc()).limit(1)

    @staticmethod
    def get_latest_ids_fielding(target_team, target_cs):
        """
            Get latest IDS fielding for provided team and CS.
        :param target_team: Team for which IDS fielding need to be fetched.
        :param target_cs: CS for which IDS fielding need to be fetched.
        :return: list containing latest IDS fielding.
        """

        query = IDSRuleFielding.select()\
                               .join(Round, on=(IDSRuleFielding.available_round == Round.id))\
                               .join(IDSRule, on=(IDSRuleFielding.ids_rule == IDSRule.id))
        predicate = (IDSRuleFielding.team == target_team) & (IDSRule.cs == target_cs)
        return query.where(predicate).order_by(Round.num.desc()).limit(1)
