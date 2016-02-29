#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module containing the BaseStrategy."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import time

from farnsworth_client.models.challenge_binary_node import ChallengeBinaryNode
import meister.log

LOG = meister.log.LOG.getChild('strategies')


class BaseStrategy(object):
    """Base strategy.

    All other scheduling strategies should inherit from this Strategy.
    """

    def __init__(self, cgc, sleepytime=3):
        """Construct a base strategy object.

        The Base Strategy assumes that the Farnsworth API is setup already,
        and uses it directly.

        :argument cgc: a CGCAPI object, so that we can talk to the CGC API.
        :keyword sleepytime: the amount to sleep between strategy runs.
        """
        self.cgc = cgc
        self.sleepytime = sleepytime

    def sleep(self):
        """Sleep a pre-defined interval."""
        time.sleep(self.sleepytime)

    @property
    def round(self):
        """Return the number of the active round."""
        return self.cgc.status()['round']

    def cbns(self, round_=None):
        """Return the list of binaries that are active in a round.

        :keyword round_: The round number for which the binaries should be
                         returned (default: current round).
        """
        if round_ is None:
            round_ = self.round

        for binary in self.cgc.binaries(round_)['binaries']:
            cbid = binary['cbid']
            cbn = ChallengeBinaryNode.find_by(name=cbid)
            if cbn is None:
                blob = base64.b64decode(binary['data'])
                cbn = ChallengeBinaryNode.create(name=cbid, blob=blob)
            LOG.debug("Yielding %s", cbid)
            yield cbn
