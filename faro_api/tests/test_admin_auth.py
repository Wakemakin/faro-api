import json
import logging
import unittest

import faro_api

logger = logging.getLogger("faro_api."+__name__)


class AdminNoAuthTest(unittest.TestCase):

    def setUp(self):
        auth = "faro_api.middleware.auth.authtest.TestNoAuth"
        self.app = faro_api.app(testing=True, auth_strategy=auth)
        self.client = self.app.test_client()

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def test_get_empty_users(self):
        rv = self.client.get('/users')
        self.assertEqual(rv.status_code, 403)

    def test_post_user(self):
        rv = self.client.post('/users', data=json.dumps(
                              {'username': 'test',
                               'first_name': 'test-first',
                               'last_name': 'test-last'}
                              ), follow_redirects=True)
        self.assertTrue(rv.status_code == 403)

    def test_put_user_with_firstname(self):
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'first_name': 'new_name'}
                             ), follow_redirects=True)
        self.assertTrue(rv.status_code == 403)

    def test_delete_user_by_id(self):
        id = "test_user"
        rv = self.client.delete('/users/'+id, follow_redirects=True)
        self.assertTrue(rv.status_code == 403)


class ExpiredAuthTest(unittest.TestCase):

    def setUp(self):
        auth = "faro_api.middleware.auth.authtest.TestExpiredAuth"
        self.app = faro_api.app(testing=True, auth_strategy=auth)
        self.client = self.app.test_client()

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def test_get_empty_users(self):
        rv = self.client.get('/users')
        self.assertEqual(rv.status_code, 403)

    def test_post_user(self):
        rv = self.client.post('/users', data=json.dumps(
                              {'username': 'test',
                               'first_name': 'test-first',
                               'last_name': 'test-last'}
                              ), follow_redirects=True)
        self.assertTrue(rv.status_code == 403)

    def test_put_user_with_firstname(self):
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'first_name': 'new_name'}
                             ), follow_redirects=True)
        self.assertTrue(rv.status_code == 403)

    def test_delete_user_by_id(self):
        id = "test_user"
        rv = self.client.delete('/users/'+id, follow_redirects=True)
        self.assertTrue(rv.status_code == 403)
