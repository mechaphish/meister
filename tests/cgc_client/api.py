#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the CGC API client."""

import nose.tools
import responses
# Disabling no-member because responses does magic and pylint does not detect it
# pylint: disable=no-member

from meister.cgc_client.api import CGCAPI
from meister.cgc_client.errors import CGCAPIError


class TestAPI(object):

    """Test the CGC API client."""

    API_BASE_URL = 'http://ti.cgc.test'

    @responses.activate
    def test_failing_authentication(self):
        """Test that authentication fails for incorrect credentials."""
        responses.add(responses.GET, self.API_BASE_URL + '/status', status=401)
        api = CGCAPI(self.API_BASE_URL, 'user', 'wrong_pw', '/tmp/cgc')
        nose.tools.assert_raises(CGCAPIError, api.status)

    @responses.activate
    def test_api_status(self):
        """Test if the API responds with the correct status."""
        expected = {"round": 1,
                    "scores": [{"team": 1, "rank": 1, "score": 10},
                               {"team": 2, "rank": 2, "score": 9}]}
        responses.add(responses.GET, self.API_BASE_URL + '/status',
                      json=expected, status=200)
        api = CGCAPI(self.API_BASE_URL, 'user', 'pw', '/tmp/cgc')
        data = api.status()
        assert data == expected
