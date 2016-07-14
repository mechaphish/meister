#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import os

from farnsworth.models import ChallengeBinaryNode, ChallengeSet

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

    def cbns(self, round_=None):
        """Return the list of binaries that are active in a round.

        :keyword round_: The round number for which the binaries should be
                         returned (default: current round).
        """
        if round_ is None:
            round_ = self.cgc.getRound()

        LOG.debug("Fetching binaries for round %s", round_)
        for binary in self.cgc.getBinaries(round_):
            cbid = binary['cbid']
            csid = binary['csid']
            sha256 = binary['hash']
            # Note: this has to run single-threaded, otherwise we might add the
            # same binary twice to the database.
            try:
                cbn = ChallengeBinaryNode.get(ChallengeBinaryNode.sha256 == sha256)
            except ChallengeBinaryNode.DoesNotExist:
                tmp_path = os.path.join("/tmp", "{}-{}-{}".format(round_, csid, cbid))
                binary = self.cgc._get_dl(binary['uri'], tmp_path, binary['hash'])
                with open(tmp_path, 'rb') as f:
                    blob = f.read()
                os.remove(tmp_path)
                cs, _ = ChallengeSet.get_or_create(name=csid)
                cbn = ChallengeBinaryNode.create(name=cbid, cs=cs, blob=blob, sha256=sha256)
            LOG.debug("Found cbid: %s", cbid)
            yield cbn
