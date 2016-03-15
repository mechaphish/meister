#!/usr/bin/env python

from farnsworth import Feedback, Score, Evaluation, Team
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('feedback')

class Evaluator(object):

    def __init__(self, cgc, round_):
        self._cgc = cgc
        self._round = round_

    def _get_feedbacks(self):
        LOG.debug("Getting feedback")
        try:
            polls = self._cgc.getFeedback('poll', self._round.num)
            povs = self._cgc.getFeedback('pov', self._round.num)
            cbs = self._cgc.getFeedback('cb', self._round.num)
            Feedback.create(polls=polls, povs=povs, cbs=cbs, round=self._round)
        except TiError as e:
            LOG.error("Feedback cbs error: %s", e.message)


    def _get_scores(self):
        LOG.debug("Getting scores")
        try:
            scores = self._cgc.getStatus()['scores']
        except TiError as e:
            LOG.error("Scores error: %s", e.message)

        Score.create(scores=scores, round=self._round)

    def _get_consensus_evaluation(self):
        for team_id in self._cgc.getTeams():
            team = Team.find_or_create(team_id)
            LOG.debug("Getting consensus evaluation for team %s", )
            try:
                cbs = self._cgc.getEvaluation('cb', self._round.num, team.name)
                ids = self._cgc.getEvaluation('ids', self._round.num, team.name)
                Evaluation.create(cbs=cbs, ids=ids, team=team, round=self._round)
            except TiError as e:
                LOG.error("IDS error: %s", e.message)

    def run(self):
        self._get_feedbacks()
        self._get_scores()
        self._get_consensus_evaluation()
