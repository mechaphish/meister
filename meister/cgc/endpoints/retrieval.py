import json
import os
import glob
import operator

from meister.cgc.tierror import TiError

class TiRetrieval(object):
    def ready(self):
        try:
            self.getRound()
            return True
        except TiError as e:
            self._LOG.warning("CGC API is down: %s", e.message)
            return False

    def getBinaries(self, round_n):    # pylint: disable=unused-argument
        """Return all available binaries."""
        self._LOG.debug("Fetching binaries for round %s", round_n)
        return self.getEvaluation('cb', round_n, self.user_id())

    def getTeams(self):
        """ get list of teams"""
        status = self.getStatus()

        ret = []
        for team_t in status['scores']:
            ret.append(team_t['team'])

        ret.sort()
        return ret

    def getRound(self):
        """ get the current round """

        status = self.getStatus()
        return status['round']

    def getCounts(self):
        """ get dict of counts """
        ret = {}

        status = self.getStatus()

        ret['team'] = len(status['scores'])
        ret['round'] = status['round']

        pov_feedback = self.getFeedback('pov', status['round'])
        ret['pov'] = len(pov_feedback)

        poll_feedback = self.getFeedback('poll', status['round'])
        ret['poll'] = len(poll_feedback)

        cb_feedback = self.getFeedback('cb', status['round'])
        ret['cb'] = len(cb_feedback)

        return ret

    def validate_round(self, round_id):
        try:
            round_id = int(round_id)
        except ValueError:
            raise TiError('invalid round')

        if round_id < 0 or round_id > self.getRound():
            raise TiError('invalid round')

        return round_id

    def getEvaluation(self, type_id, round_id, team):
        """ get feedback dict for type (cb,pov,poll) """

        if type_id not in ['cb', 'ids']:
            raise TiError('invalid evaluation type: %s' % type_id)

        round_id = self.validate_round(round_id)

        uri = "/round/%d/evaluation/%s/%s" % (round_id, type_id, team)
        status, reason, body = self._make_request(uri)

        try:
            data = json.loads(body)
        except ValueError:
            raise TiError('unable to parse server response')

        return data[type_id]

    def getFeedback(self, feedback_type, round_id):
        """ get feedback dict for type (cb,pov,poll) """

        round_id = self.validate_round(round_id)
        if feedback_type not in ['pov', 'cb', 'poll']:
            raise TiError('invalid feedback type: %s' % feedback_type)

        uri = "/round/%d/feedback/%s" % (round_id, feedback_type)

        status, reason, body = self._make_request(uri)

        try:
            data = json.loads(body)
        except ValueError:
            raise TiError('unable to parse server response')

        return data[feedback_type]

    def getScores(self, byscore=True):
        """ get list of scores """
        status = self.getStatus()
        data = {}

        for team in status['scores']:
            data[team['team']] = team['score']

        if byscore:
            ret = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
        else:
            ret = sorted(data.items(), key=operator.itemgetter(0))

        return ret

    def getConsensus(self, csid, data_type, team, round_id, output_dir):
        if not os.path.isdir(output_dir):
            raise TiError('output directory is not a directory')

        types = ['cb', 'ids']
        if data_type not in types:
            raise TiError('invalid consensus type')

        response = self.getEvaluation(data_type, round_id, team)

        paths = []

        for entry in response:
            if csid != entry['csid']:
                continue
            if data_type == 'cb':
                paths.append((entry['cbid'], entry['uri'], entry['hash']))
            else:
                paths.append((csid, entry['uri'], entry['hash']))

        if not len(paths):
            raise TiError('invalid csid')

        files = []

        for entry in paths:
            cbid, uri, checksum = entry
            filename = '%s-%s-%s.%s' % (cbid, team, round_id, data_type)
            path = os.path.join(output_dir, filename)
            self._get_dl(uri, path, checksum)
            files.append(path)

        files.sort()

        return files

    def getStatus(self):
        """
        issues HTTP GET to retreive CGC CFE status (teams, scores, current round id)
        """

        uri = "/status"

        status, reason, body = self._make_request(uri)

        try:
            status = json.loads(body)
        except ValueError:
            raise TiError('unable to parse server response')

        return status
