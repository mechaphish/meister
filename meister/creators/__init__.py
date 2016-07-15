#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import os

from farnsworth.models import ChallengeBinaryNode, ChallengeSet, ChallengeSetFielding, Round, Team

import meister.log
LOG = meister.log.LOG.getChild('creators')

"""Job creator."""


class BaseCreator(object):
    """Abstract creator class, should be inherited by actual job creators."""

    def __init__(self, cgc):
        """Create base creator.

        Create the base creator, you should call this from your creator to
        make sure that all class variables are set up properly.
        """
        self.cgc = cgc

    @property
    def jobs(self):
        raise NotImplementedError("You have to implemented the jobs property")

    def challenge_sets(self, round_=None):
        """Return the list of challenge sets that are active in a round.

        :keyword round_: The round number for which the binaries should be
                         returned (default: current round).
        """
        # FIXME: Why are we not doing return set(csids)?
        csids = [cbn.cs.id for cbn in self.cbns(round_)]
        return ChallengeSet.select().where(ChallengeSet.id << csids)

    def single_cb_challenge_sets(self, round_=None):
        """Return the list of single-cb challenge sets that are active in a round.

        :keyword round_: The round number for which the binaries should be
                         returned (default: current round).
        """
        csids = [cbn.cs.id for cbn in self.cbns(round_) if not cbn.cs.is_multi_cbn]
        return ChallengeSet.select().where(ChallengeSet.id << csids)

    def cbns(self, round_=None):
        """Return the list of binaries that are active in a round.

        :keyword round_: The round number for which the binaries should be
                         returned (default: current round).
        """
        if round_ is None:
            round_, _ = Round.get_or_create(num=self.cgc.getRound())

        LOG.debug("Fetching binaries for round %s", round_)
        binaries = self.cgc.getBinaries(round_.num)
        for binary in binaries:
            cbid = binary['cbid']
            csid = binary['csid']
            sha256 = binary['hash']
            # Note: this has to run single-threaded, otherwise we might add the
            # same binary twice to the database.
            try:
                cbn = ChallengeBinaryNode.get(ChallengeBinaryNode.sha256 == sha256)
            except ChallengeBinaryNode.DoesNotExist:
                tmp_path = os.path.join("/tmp", "{}-{}-{}".format(round_.num, csid, cbid))
                binary = self.cgc._get_dl(binary['uri'], tmp_path, binary['hash'])
                with open(tmp_path, 'rb') as f:
                    blob = f.read()
                os.remove(tmp_path)
                cs, _ = ChallengeSet.get_or_create(name=csid)
                cbn = ChallengeBinaryNode.create(name=cbid, cs=cs, blob=blob, sha256=sha256)
            try:
                team, _ = Team.get_or_create(name=Team.OUR_NAME)
                csf = ChallengeSetFielding.get((ChallengeSetFielding.cs == cbn.cs) & \
                                               (ChallengeSetFielding.team == team) & \
                                               (ChallengeSetFielding.available_round == round_))
                csf.add_cbns_if_missing(cbn)
            except ChallengeSetFielding.DoesNotExist:
                csf = ChallengeSetFielding.create(cs=cbn.cs, team=team, cbns=[cbn], available_round=round_)

            LOG.debug("Found cbid: %s", cbid)
            yield cbn
