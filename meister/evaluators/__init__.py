#!/usr/bin/env python

from farnsworth.models import Feedback, Score, Evaluation, Team
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('feedback')

class Evaluator(object):

    def __init__(self, cgc, round_):
        self._cgc = cgc
        self._round = round_

    def _get_feedbacks(self):
        LOG.debug("Getting feedback")
        polls, povs, cbs = {}, {}, {}
        try:
            polls = self._cgc.getFeedback('poll', self._round.num)
        except TiError as e:
            LOG.error("Feedback poll error: %s", e.message)
        try:
            povs = self._cgc.getFeedback('pov', self._round.num)
        except TiError as e:
            LOG.error("Feedback pov error: %s", e.message)
        try:
            cbs = self._cgc.getFeedback('cb', self._round.num)
        except TiError as e:
            LOG.error("Feedback cb error: %s", e.message)
        Feedback.update_or_create(self._round, polls=polls, povs=povs, cbs=cbs)


    def _get_scores(self):
        LOG.debug("Getting scores")
        scores = {}
        try:
            scores = self._cgc.getStatus()['scores']
        except TiError as e:
            LOG.error("Scores error: %s", e.message)
        Score.update_or_create(self._round, scores=scores)


    def _get_consensus_evaluation(self):
        try:
            for team_id in self._cgc.getTeams():
                team = Team.find_or_create(name = team_id)
                LOG.debug("Getting consensus evaluation for team %s", team_id)
                cbs, ids = {}, {}
                try:
                    cbs = self._cgc.getEvaluation('cb', self._round.num, team.name)
                except TiError as e:
                    LOG.error("Consensus evaluation error: %s", e.message)
                try:
                    ids = self._cgc.getEvaluation('ids', self._round.num, team.name)
                except TiError as e:
                    LOG.error("Consensus evaluation error: %s", e.message)
                Evaluation.update_or_create(self._round, team, cbs=cbs, ids=ids)
        except TiError as e:
            LOG.error("Unable to get teams: %s", e.message)


    def run(self):
        self._get_feedbacks()
        self._get_scores()
        self._get_consensus_evaluation()
