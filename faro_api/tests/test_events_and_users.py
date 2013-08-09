import json
import logging
import unittest

import faro_api
from faro_common import utils

logger = logging.getLogger("faro_api."+__name__)


class EventAndUserTest(unittest.TestCase):

    def setUp(self):
        self.app = faro_api.app(testing=True)
        self.client = self.app.test_client()

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def create_user(self, name):
        return self.client.post('/users', data=json.dumps(
                                {'username': name}
                                ), follow_redirects=True)

    def create_event_with_user(self, username, eventname):
        rv = self.create_user(username)
        rv = self.client.post('/events', data=json.dumps(
                              {'name': 'test',
                                  'owner_id': username}
                              ), follow_redirects=True)
        return rv

    def test_create_event_with_owner_id(self):
        rv = self.create_user('test_user')
        self.assertTrue(rv.status_code == 201)
        res = json.loads(rv.data)
        user_id = res['id']
        rv = self.client.post('/events', data=json.dumps(
                              {'name': 'test',
                                  'owner_id': user_id}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue('owner' in res)
        self.assertTrue(res['owner']['username'] == 'test_user')
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))
        self.assertTrue(rv.status_code == 201)

    def test_create_event_with_owner_name(self):
        rv = self.create_user('test_user')
        self.assertTrue(rv.status_code == 201)
        rv = self.client.post('/events', data=json.dumps(
                              {'name': 'test',
                                  'owner_id': 'test_user'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue('owner' in res)
        self.assertTrue(res['owner']['username'] == 'test_user')
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))
        self.assertTrue(rv.status_code == 201)

    def test_get_owner_of_event(self):
        rv = self.create_event_with_user('test_user', 'event')
        self.assertTrue(rv.status_code == 201)
        res = json.loads(rv.data)
        event_id = res['id']
        rv = self.client.get('/events/%s/owner' % event_id,
                             follow_redirects=True)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(res['object']['username'] == 'test_user')

    def test_get_no_events_under_user(self):
        rv = self.create_user('test_user')
        self.assertTrue(rv.status_code == 201)
        rv = self.client.get('/users/test_user/events',
                             follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(res['objects']) == 0)

    def test_get_events_under_user(self):
        rv = self.create_event_with_user('test_user', 'event')
        self.assertTrue(rv.status_code == 201)
        rv = self.create_event_with_user('test_user2', 'event')
        self.assertTrue(rv.status_code == 201)
        rv = self.client.get('/users/test_user/events',
                             follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(res['objects']) == 1)

    def test_create_event_under_user(self):
        rv = self.create_user('test_user')
        self.assertTrue(rv.status_code == 201)
        rv = self.client.post('/users/test_user/events',
                              data=json.dumps(
                                  {'name': 'test'}),
                              follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(rv.status_code == 201)
        self.assertTrue('owner' in res)
        self.assertTrue(res['owner']['username'] == 'test_user')
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))

    def test_error_put_event_good_username(self):
        rv = self.create_event_with_user("test_user", "event")
        self.assertTrue(rv.status_code == 201)
        res = json.loads(rv.data)
        event_id = res['id']
        rv = self.create_user('test_user2')
        res = json.loads(rv.data)
        new_user_id = res['id']
        rv = self.client.put('/events/'+event_id, data=json.dumps(
                             {'owner_id': 'test_user2'}
                             ), follow_redirects=True)
        rv = self.client.get('/events/'+event_id,
                             follow_redirects=True)
        self.assertTrue(rv.status_code == 200)
        res = json.loads(rv.data)
        self.assertTrue(new_user_id == res['object']['owner']['id'])

    def test_error_get_owner_of_bad_event(self):
        id = str(utils.make_uuid())
        rv = self.client.get('/events/%s/owner' % id,
                             follow_redirects=True)
        self.assertTrue(rv.status_code == 404)

    def test_error_get_events_of_bad_owner(self):
        rv = self.client.get('/users/%s/events' % 'derp',
                             follow_redirects=True)
        self.assertTrue(rv.status_code == 404)

    def test_error_put_event_bad_username(self):
        rv = self.create_event_with_user("test_user", "event")
        self.assertTrue(rv.status_code == 201)
        res = json.loads(rv.data)
        event_id = res['id']
        owner_id = res['owner']['id']
        rv = self.client.put('/events/'+event_id, data=json.dumps(
                             {'owner_id': 'missing_user'}
                             ), follow_redirects=True)
        self.assertTrue(rv.status_code == 404)
        rv = self.client.get('/events/'+event_id,
                             follow_redirects=True)
        self.assertTrue(rv.status_code == 200)
        res = json.loads(rv.data)
        self.assertTrue(owner_id == res['object']['owner']['id'])

    def test_error_create_event_bad_user_name(self):
        rv = self.client.post('/events', data=json.dumps(
                              {'name': 'test',
                                  'owner_id': 'test_user'}
                              ), follow_redirects=True)
        self.assertTrue(rv.status_code == 404)

    def test_error_create_event_bad_user_id(self):
        rv = self.client.post('/events', data=json.dumps(
                              {'name': 'test',
                                  'owner_id': str(utils.make_uuid())}
                              ), follow_redirects=True)
        self.assertTrue(rv.status_code == 404)

    def test_regression_delete_user_with_event_fail(self):
        rv = self.create_event_with_user('test_user', 'event')
        self.assertTrue(rv.status_code == 201)
        rv = self.client.delete('/users/test_user',
                                follow_redirects=True)
        self.assertTrue(rv.status_code == 204)

    def test_regression_delete_user_with_event_fail_delete_event(self):
        rv = self.create_event_with_user('test_user', 'event')
        self.assertTrue(rv.status_code == 201)
        res = json.loads(rv.data)
        event_id = res['id']
        rv = self.client.delete('/events/%s' % event_id,
                                follow_redirects=True)
        self.assertTrue(rv.status_code == 204)
        rv = self.client.delete('/users/test_user',
                                follow_redirects=True)
        self.assertTrue(rv.status_code == 204)
