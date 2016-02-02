import nose
from nose.tools import *
import responses

from meister.cgc_client import API
from meister.cgc_client.errors import *

class TestAPI:
    API_BASE_URL = 'http://ti.cgc.test'

    @responses.activate
    def test_failing_authentication(self):
        responses.add(responses.GET, self.API_BASE_URL + '/status', status=401)
        api = API(self.API_BASE_URL, 'user', 'wrong_pw')
        assert_raises(APIError, api.status)

    @responses.activate
    def test_api_status(self):
        expected = {
            "round": 1,
            "scores": [
                {"team": 1, "rank": 1, "score": 10},
                {"team": 2, "rank": 2, "score": 9}
            ]
        }
        responses.add(responses.GET, self.API_BASE_URL + '/status',
                      json=expected, status=200)
        api = API(self.API_BASE_URL, 'user', 'pw')
        data = api.status()
        assert data == expected
