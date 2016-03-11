#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Job creator."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import base64

from farnsworth.models.challenge_binary_node import ChallengeBinaryNode
import meister.log

LOG = meister.log.LOG.getChild('creators')


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

    def cbns(self, round_=None):
        """Return the list of binaries that are active in a round.

        :keyword round_: The round number for which the binaries should be
                         returned (default: current round).
        """
        if round_ is None:
            round_ = self.cgc.getRound()

        LOG.debug("Fetching binaries for round %s", round_)

        for binary in self.cgc.getBinaries(round_)['binaries']:
            cbid = binary['cbid']
            # Note: this has to run single-threaded, otherwise we might add the
            # same binary twice to the database.
            try:
                cbn = ChallengeBinaryNode.get(ChallengeBinaryNode.name == cbid)
            except ChallengeBinaryNode.DoesNotExist:
                blob = base64.b64decode(binary['data'])
                csid = cbid.split('_', 1)[0]
                cbn = ChallengeBinaryNode(name=cbid, cs_id=csid, blob=blob)
                cbn.save()
            LOG.debug("Found cbid: %s", cbid)
            yield cbn
