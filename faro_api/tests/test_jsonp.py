import json
import logging
import unittest

import faro_api

logger = logging.getLogger("faro_api."+__name__)


class UserTest(unittest.TestCase):

    def setUp(self):
        auth = "faro_api.middleware.auth.authtest.TestAdminAuth"
        self.app = faro_api.app(testing=True, auth_strategy=auth)
        self.client = self.app.test_client()

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def create_user(self, name):
        return self.client.post('/users', data=json.dumps(
                                {'username': name}
                                ), follow_redirects=True)

    def test_ensure_jsonp_wraps(self):
        rv = self.client.get('/users?callback=foo')
        self.assertTrue('foo(' in rv.data)
        self.assertTrue('});' in rv.data)
        mod_data = rv.data.replace('foo(', '')
        mod_data = mod_data.replace(');', '')
        rv = self.client.get('/users')
        self.assertTrue(rv.data == mod_data)
        res = json.loads(mod_data)
        self.assertTrue(res['objects'] == [])
        self.assertTrue(rv.status_code == 200)

    def test_ensure_jsonp_uses_callback(self):
        rv = self.client.get('/users?callback=foo')
        self.assertTrue('foo(' in rv.data)
        rv = self.client.get('/users?callback=bar')
        self.assertTrue('bar(' in rv.data)
