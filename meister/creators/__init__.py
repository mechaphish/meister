#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import os

from farnsworth.models import ChallengeBinaryNode, ChallengeSet, ChallengeSetFielding, Round, Team
import stopit

import meister.log
LOG = meister.log.LOG.getChild('creators')

JOBS_TIME_LIMIT = 30

"""Job creator."""


class BaseCreator(object):
    """Abstract creator class, should be inherited by actual job creators."""

    def __init__(self):
        """Create base creator.

        Create the base creator, you should call this from your creator to
        make sure that all class variables are set up properly.
        """
        pass

    @property
    def _jobs(self):
        raise NotImplementedError("You have to implemented the jobs property")

    @property
    def jobs(self):
        yielded = False
        try:
            with stopit.ThreadingTimeout(JOBS_TIME_LIMIT, swallow_exc=False):
                for job_priority in self._jobs:
                    # Pass through the actual job priority tuple
                    yielded = True
                    yield job_priority
        except Exception, e:
            # Pokemon Exception Handling to reduce impact of bad creators.
            LOG.error("%s failed with %s: %s", self.__class__.__name__, e.__class__.__name__, e)
            if not yielded:
                raise StopIteration()

    def challenge_sets(self, round_=None):
        """Return the list of challenge sets that are active in a round.

        :keyword round_: The round number for which the binaries should be
                         returned (default: current round).
        """
        return ChallengeSet.fielded_in_round(round_)

    def single_cb_challenge_sets(self, round_=None):
        """Return the list of single-cb challenge sets that are active in a round.

        :keyword round_: The round number for which the binaries should be
                         returned (default: current round).
        """
        csids = [cbn.cs.id for cbn in self.cbns(round_) if not cbn.cs.is_multi_cbn]
        if csids:
            return ChallengeSet.select().where(ChallengeSet.id << csids)
        else:
            return []

    def cbns(self, round_=None):
        """Return the list of binaries that are active in a round.

        :keyword round_: The round instance for which the binaries should be
                         returned (default: current round).
        """
        for cs in ChallengeSet.fielded_in_round(round_):
            for cbn in cs.cbns_original:
                LOG.debug("Found cbid: %s", cbn.name)
                yield cbn
