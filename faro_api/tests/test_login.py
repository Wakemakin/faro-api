import json
import logging
import unittest

import faro_api

logger = logging.getLogger("faro_api."+__name__)


class LoginTokenTest(unittest.TestCase):

    def setUp(self):
        auth = "faro_api.middleware.auth.authtest.TestTogglingAuth"
        self.app = faro_api.app(testing=True, auth_strategy=auth)
        self.client = self.app.test_client()
        self._create_test_environment()

    def _create_test_environment(self):
        headers = [('X-Auth-Token', 'ABC123')]
        rv = self.client.post('/users', data=json.dumps(
                              {'username': 'test1',
                               'first_name': 'test-first',
                               'last_name': 'test-last'}
                              ), follow_redirects=True, headers=headers)
        res = json.loads(rv.data)
        self.user1 = res
        self.headers1 = [('X-Auth-Id', self.user1['id'])]
        rv = self.client.post('/users', data=json.dumps(
                              {'username': 'test2',
                               'first_name': 'test-first',
                               'last_name': 'test-last'}
                              ), follow_redirects=True, headers=headers)
        res = json.loads(rv.data)
        self.user2 = res
        self.headers2 = [('X-Auth-Id', self.user2['id'])]

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def test_get_tokens(self):
        rv = self.client.get('/tokens', headers=self.headers1)
        self.assertEquals(200, rv.status_code)

    def test_get_token(self):
        rv = self.client.get('/tokens/randomid', headers=self.headers1)
        self.assertEquals(405, rv.status_code)

    def test_put_tokens(self):
        rv = self.client.put('/tokens')
        self.assertEquals(405, rv.status_code)

    def test_post_token_valid(self):
        rv = self.client.post('/tokens', data=json.dumps(
                              {'username': 'test1', 'password': 'password'}),
                              follow_redirects=True)
        self.assertEquals(201, rv.status_code)
