#!/usr/bin/env python

from farnsworth import Feedback
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('feedback')

class Evaluator(object):

    def __init__(self, cgc, round_):
        self._cgc = cgc
        self._round = round_

    def run(self):
        LOG.debug("Getting feedback")
        try:
            polls = self._cgc.getFeedback('poll', self._round.num)
        except TiError as e:
            LOG.error("Feedback polls error: %s", e.message)
        try:
            povs = self._cgc.getFeedback('pov', self._round.num)
        except TiError as e:
            LOG.error("Feedback povs error: %s", e.message)
        try:
            cbs = self._cgc.getFeedback('cb', self._round.num)
        except TiError as e:
            LOG.error("Feedback cbs error: %s", e.message)

        Feedback.create(polls=polls, povs=povs, cbs=cbs, round=self._round)
