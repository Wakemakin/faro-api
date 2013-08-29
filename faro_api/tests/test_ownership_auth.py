import json
import logging
import unittest

import faro_api
import faro_common.utils as utils

logger = logging.getLogger("faro_api."+__name__)


class OwnershipAuthTest(unittest.TestCase):

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

    def _create_event_under_owner1(self):
        id = self.user1['id']
        uri = '/users/%s/events' % id
        rv = self.client.post(uri, data=json.dumps({'name': 'test'}),
                              follow_redirects=True, headers=self.headers1)
        res = json.loads(rv.data)
        return res

    def test_create_event_under_owner_user(self):
        id = self.user1['id']
        uri = '/users/%s/events' % id
        rv = self.client.post(uri, data=json.dumps({'name': 'test'}),
                              follow_redirects=True, headers=self.headers1)
        res = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        self.assertTrue('owner' in res)
        self.assertTrue(res['owner']['username'] == self.user1['username'])
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))

    def test_create_event_under_wrong_user(self):
        id = self.user1['id']
        uri = '/users/%s/events' % id
        rv = self.client.post(uri, data=json.dumps({'name': 'test'}),
                              follow_redirects=True, headers=self.headers2)
        self.assertEqual(rv.status_code, 404)

    def test_get_empty_event_under_owner_user(self):
        id = self.user1['id']
        uri = '/users/%s/events' % id
        rv = self.client.get(uri, headers=self.headers1)
        self.assertEqual(rv.status_code, 200)

    def test_get_empty_event_under_wrong_user(self):
        id = self.user1['id']
        uri = '/users/%s/events' % id
        rv = self.client.get(uri, headers=self.headers2)
        self.assertEqual(rv.status_code, 404)

    def test_get_an_event_under_owner_user(self):
        self._create_event_under_owner1()
        id = self.user1['id']
        uri = '/users/%s/events' % id
        rv = self.client.get(uri, headers=self.headers1)
        self.assertEqual(rv.status_code, 200)
        res = json.loads(rv.data)
        self.assertEqual(1, len(res['objects']))

    def test_get_an_event_under_wrong_user(self):
        self._create_event_under_owner1()
        id = self.user1['id']
        uri = '/users/%s/events' % id
        rv = self.client.get(uri, headers=self.headers2)
        self.assertEqual(rv.status_code, 404)

    def test_put_an_event_under_owner_user(self):
        event = self._create_event_under_owner1()
        event_id = event['id']
        uri = '/events/%s' % event_id
        rv = self.client.put(uri, data=json.dumps({'description': 'test'}),
                             follow_redirects=True, headers=self.headers1)
        self.assertEqual(rv.status_code, 200)

    def test_put_an_event_under_wrong_user(self):
        event = self._create_event_under_owner1()
        event_id = event['id']
        uri = '/events/%s' % event_id
        rv = self.client.put(uri, data=json.dumps({'description': 'test'}),
                             follow_redirects=True, headers=self.headers2)
        self.assertEqual(rv.status_code, 404)
