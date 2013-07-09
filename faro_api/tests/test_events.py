import unittest
import logging
import json

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

    def create_event(self, name):
        return self.client.post('/api/events', data=json.dumps(
                                {'name': name}
                                ), follow_redirects=True)

    def test_get_empty_events(self):
        rv = self.client.get('/api/events')
        res = json.loads(rv.data)
        assert res['objects'] == []
        assert rv.status_code == 200

    def test_get_one_event(self):
        rv = self.create_event("test")
        rv = self.client.get('/api/events')
        res = json.loads(rv.data)
        assert len(res['objects']) == 1

    def test_get_one_event_by_id(self):
        rv = self.create_event("test")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.get('/api/events/' + id)
        res = json.loads(rv.data)
        assert res['objects']['name'] == 'test'
        assert res['objects']['id'] == id

    def test_get_multi_user(self):
        rv = self.create_event("test1")
        rv = self.create_event("test2")
        rv = self.client.get('/api/events')
        res = json.loads(rv.data)
        assert len(res['objects']) == 2

    def test_post_event_just_name(self):
        rv = self.client.post('/api/events', data=json.dumps(
                              {'name': 'test'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['name'] == 'test'
        assert res['id'] is not None
        assert utils.is_uuid(res['id'])
        assert rv.status_code == 201

    def test_post_event(self):
        rv = self.client.post('/api/events', data=json.dumps(
                              {'name': 'test',
                              'description': 'derp'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['name'] == 'test'
        assert res['id'] is not None
        assert utils.is_uuid(res['id'])
        assert rv.status_code == 201

    def test_post_event_with_id(self):
        """Should this test fail?"""
        rv = self.client.post('/api/events', data=json.dumps(
                              {'name': 'test',
                              'id': 'test-id',
                              'description': 'derp'}
                              ), follow_redirects=True)
        assert rv.status_code == 201

    def test_put_event_with_name(self):
        rv = self.create_event('test_event')
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
        rv = self.create_event('test_event')
        res = json.loads(rv.data)
        id = res['id']
        assert res['description'] is None
        rv = self.client.put('/api/events/'+id, data=json.dumps(
                             {'description': 'test'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['description'] == 'test'
        assert rv.status_code == 200

    def test_delete_event(self):
        rv = self.create_event("test")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.delete('/api/events/'+id, follow_redirects=True)
        assert rv.status_code == 204

    def test_error_get_one_event_by_fail_id(self):
        id = str(utils.make_uuid())
        rv = self.client.get('/api/events/'+id)
        assert rv.status_code == 404

    def test_error_post_event_with_made_event(self):
        rv = self.create_event("test")
        id = json.loads(rv.data)['id']
        rv = self.client.post('/api/events/'+id, data=json.dumps(
                              {'name': 'test'}
                              ), follow_redirects=True)
        assert rv.status_code == 405

    def test_error_put_event_with_id(self):
        rv = self.create_event("test")
        id = json.loads(rv.data)['id']
        rv = self.client.put('/api/events/'+id, data=json.dumps(
                             {'id': 'test'}
                             ), follow_redirects=True)
        assert rv.status_code == 403

    def test_error_delete_fail_event(self):
        id = str(utils.make_uuid())
        rv = self.client.delete('/api/events/'+id)
        assert rv.status_code == 404
