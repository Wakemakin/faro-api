import json
import logging
import unittest

import faro_api
from faro_api import utils

logger = logging.getLogger("faro_api."+__name__)


class EventTest(unittest.TestCase):

    def setUp(self):
        self.app = faro_api.app(testing=True)
        self.client = self.app.test_client()

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def create_user(self, name):
        return self.client.post('/api/users', data=json.dumps(
                                {'username': name}
                                ), follow_redirects=True)

    def create_event_with_user(self, name, username='test_user'):
        self.create_user(username)
        return self.client.post('/api/events', data=json.dumps(
                                {'name': name,
                                'owner_id': username}
                                ), follow_redirects=True)

    def test_get_empty_events(self):
        rv = self.client.get('/api/events')
        res = json.loads(rv.data)
        assert res['objects'] == []
        assert rv.status_code == 200

    def test_get_one_event(self):
        rv = self.create_event_with_user("test")
        rv = self.client.get('/api/events')
        res = json.loads(rv.data)
        assert len(res['objects']) == 1

    def test_get_one_event_by_id(self):
        rv = self.create_event_with_user("test")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.get('/api/events/' + id)
        res = json.loads(rv.data)
        assert res['object']['name'] == 'test'
        assert res['object']['id'] == id

    def test_get_multi_user(self):
        rv = self.create_event_with_user("test1")
        rv = self.create_event_with_user("test2")
        rv = self.client.get('/api/events')
        res = json.loads(rv.data)
        assert len(res['objects']) == 2

    def test_post_event_just_name(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/api/events', data=json.dumps(
                              {'name': 'test',
                              'owner_id': 'test_user'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['name'] == 'test'
        assert res['id'] is not None
        assert utils.is_uuid(res['id'])
        assert rv.status_code == 201

    def test_post_event(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/api/events', data=json.dumps(
                              {'name': 'test',
                              'description': 'derp',
                              'owner_id': 'test_user'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['name'] == 'test'
        assert res['id'] is not None
        assert utils.is_uuid(res['id'])
        assert rv.status_code == 201

    def test_post_event_with_id(self):
        """Should this test fail?"""
        rv = self.create_user('test_user')
        rv = self.client.post('/api/events', data=json.dumps(
                              {'name': 'test',
                              'id': 'test-id',
                              'description': 'derp',
                              'owner_id': 'test_user'}
                              ), follow_redirects=True)
        assert rv.status_code == 201

    def test_put_event_with_name(self):
        rv = self.create_event_with_user('test_event')
        res = json.loads(rv.data)
        id = res['id']
        assert res['name'] == 'test_event'
        rv = self.client.put('/api/events/'+id, data=json.dumps(
                             {'name': 'test'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['name'] == 'test'
        assert rv.status_code == 200

    def test_put_event_with_description(self):
        rv = self.create_event_with_user('test_event')
        res = json.loads(rv.data)
        id = res['id']
        assert res['description'] is None
        rv = self.client.put('/api/events/'+id, data=json.dumps(
                             {'description': 'test'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['description'] == 'test'
        assert rv.status_code == 200

    def test_filter_event_by_owner(self):
        rv = self.create_event_with_user("test", "derp")
        rv = self.create_event_with_user("test2", "herp")
        rv = self.client.get('/api/events')
        res = json.loads(rv.data)
        assert len(res['objects']) == 2
        assert rv.status_code == 200
        rv = self.client.get('/api/events?owner_id=derp')
        res = json.loads(rv.data)
        assert len(res['objects']) == 1
        assert rv.status_code == 200

    def test_filter_event_by_name(self):
        rv = self.create_event_with_user("test", "asdf")
        rv = self.create_event_with_user("derp", "asdf2")
        rv = self.client.get('/api/events')
        res = json.loads(rv.data)
        assert len(res['objects']) == 2
        assert rv.status_code == 200
        rv = self.client.get('/api/events?name=derp')
        res = json.loads(rv.data)
        assert len(res['objects']) == 1
        assert rv.status_code == 200

    def test_delete_event(self):
        rv = self.create_event_with_user("test")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.delete('/api/events/'+id, follow_redirects=True)
        assert rv.status_code == 204

    def test_error_get_one_event_by_fail_id(self):
        id = str(utils.make_uuid())
        rv = self.client.get('/api/events/'+id)
        assert rv.status_code == 404

    def test_error_post_event_empty_body(self):
        rv = self.client.post('/api/events', data=json.dumps(
                              {}
                              ), follow_redirects=True)
        assert rv.status_code == 400

    def test_error_post_event_no_name(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/api/events', data=json.dumps(
                              {'description': 'herps and derps',
                              'owner_id': 'test_user'}
                              ), follow_redirects=True)
        assert rv.status_code == 409

    def test_error_post_event_with_made_event(self):
        rv = self.create_user('test_user')
        rv = self.create_event_with_user("test")
        id = json.loads(rv.data)['id']
        rv = self.client.post('/api/events/'+id, data=json.dumps(
                              {'name': 'test',
                              'owner_id': 'test_user'}
                              ), follow_redirects=True)
        assert rv.status_code == 405

    def test_error_put_event_with_id(self):
        rv = self.create_event_with_user("test")
        id = json.loads(rv.data)['id']
        rv = self.client.put('/api/events/'+id, data=json.dumps(
                             {'id': 'test'}
                             ), follow_redirects=True)
        assert rv.status_code == 403

    def test_error_delete_fail_event(self):
        id = str(utils.make_uuid())
        rv = self.client.delete('/api/events/'+id)
        assert rv.status_code == 404