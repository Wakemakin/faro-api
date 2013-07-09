import unittest
import logging
import json

import faro_api
from faro_api import utils

logger = logging.getLogger("faro_api."+__name__)


class UserTest(unittest.TestCase):

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

    def test_get_empty_users(self):
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        assert res['objects'] == []
        assert rv.status_code == 200

    def test_get_one_user(self):
        rv = self.create_user("test2")
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == 1

    def test_get_one_user_by_username(self):
        rv = self.create_user("test")
        rv = self.client.get('/api/users/test')
        res = json.loads(rv.data)
        assert res['object']['username'] == 'test'

    def test_get_one_user_by_id(self):
        rv = self.create_user("test")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.get('/api/users/' + id)
        res = json.loads(rv.data)
        assert res['object']['username'] == 'test'
        assert res['object']['id'] == id

    def test_get_multi_user(self):
        rv = self.create_user("test1")
        rv = self.create_user("test2")
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == 2

    def test_post_user_just_username(self):
        rv = self.client.post('/api/users', data=json.dumps(
                              {'username': 'test'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['username'] == 'test'
        assert res['first_name'] is None
        assert res['last_name'] is None
        assert res['id'] is not None
        assert utils.is_uuid(res['id'])
        assert rv.status_code == 201

    def test_post_user(self):
        rv = self.client.post('/api/users', data=json.dumps(
                              {'username': 'test',
                              'first_name': 'test-first',
                              'last_name': 'test-last'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['username'] == 'test'
        assert res['first_name'] == 'test-first'
        assert res['last_name'] == 'test-last'
        assert res['id'] is not None
        assert utils.is_uuid(res['id'])
        assert rv.status_code == 201

    def test_post_user_with_id(self):
        """Should this test fail?"""
        rv = self.client.post('/api/users', data=json.dumps(
                              {'username': 'test',
                              'id': 'test-id'}
                              ), follow_redirects=True)
        assert rv.status_code == 201

    def test_put_user_with_firstname(self):
        rv = self.create_user("test1")
        res = json.loads(rv.data)
        assert res['first_name'] is None
        rv = self.client.put('/api/users/test1', data=json.dumps(
                             {'first_name': 'new_name'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['first_name'] == 'new_name'
        assert rv.status_code == 200

    def test_filter_user_no_results(self):
        rv = self.create_user("test1")
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == 1
        rv = self.client.put('/api/users/test1', data=json.dumps(
                             {'first_name': 'test_name'}
                             ), follow_redirects=True)
        rv = self.client.get('/api/users?first_name=derp')
        res = json.loads(rv.data)
        assert res['objects'] == []
        assert len(res['objects']) == 0
        assert rv.status_code == 200

    def test_filter_user_one_results(self):
        rv = self.create_user("test1")
        rv = self.create_user("test2")
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == 2
        rv = self.client.put('/api/users/test1', data=json.dumps(
                             {'first_name': 'test_name'}
                             ), follow_redirects=True)
        rv = self.client.get('/api/users?first_name=test_name')
        res = json.loads(rv.data)
        assert len(res['objects']) == 1
        assert rv.status_code == 200

    def test_filter_user_two_results(self):
        rv = self.create_user("test1")
        rv = self.create_user("test2")
        rv = self.create_user("test3")
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == 3
        rv = self.client.put('/api/users/test2', data=json.dumps(
                             {'first_name': 'derp'}
                             ), follow_redirects=True)
        rv = self.client.put('/api/users/test1', data=json.dumps(
                             {'first_name': 'derply'}
                             ), follow_redirects=True)
        rv = self.client.put('/api/users/test3', data=json.dumps(
                             {'first_name': 'hiyo'}
                             ), follow_redirects=True)
        rv = self.client.get('/api/users?first_name=derp')
        res = json.loads(rv.data)
        assert len(res['objects']) == 2
        assert rv.status_code == 200

    def test_filter_user_and_one_results(self):
        rv = self.create_user("test1")
        rv = self.create_user("test2")
        rv = self.create_user("test3")
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == 3
        rv = self.client.put('/api/users/test2', data=json.dumps(
                             {'first_name': 'derp',
                              'last_name': 'herp'}
                             ), follow_redirects=True)
        rv = self.client.put('/api/users/test1', data=json.dumps(
                             {'first_name': 'derply',
                              'last_name': 'hiyo'}
                             ), follow_redirects=True)
        rv = self.client.put('/api/users/test3', data=json.dumps(
                             {'first_name': 'hiyo',
                              'last_name': 'herp'}
                             ), follow_redirects=True)
        rv = self.client.get('/api/users?first_name=derp&last_name=hi')
        res = json.loads(rv.data)
        assert len(res['objects']) == 1
        assert rv.status_code == 200

    def test_put_user_with_lastname(self):
        rv = self.create_user("test1")
        res = json.loads(rv.data)
        assert res['last_name'] is None
        rv = self.client.put('/api/users/test1', data=json.dumps(
                             {'last_name': 'new_name'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        assert res['last_name'] == 'new_name'
        assert rv.status_code == 200

    def test_delete_user_by_id(self):
        rv = self.create_user("test1")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.delete('/api/users/'+id, follow_redirects=True)
        assert rv.status_code == 204

    def test_delete_user_by_username(self):
        rv = self.create_user("test1")
        rv = self.client.delete('/api/users/test1', follow_redirects=True)
        assert rv.status_code == 204

    def test_error_post_dupe_username(self):
        rv = self.create_user("test1")
        rv = self.create_user("test1")
        assert rv.status_code == 409

    def test_error_get_one_user_by_fail_username(self):
        rv = self.client.get('/api/users/asdfasdf')
        assert rv.status_code == 404

    def test_error_get_one_user_by_fail_id(self):
        id = str(utils.make_uuid())
        rv = self.client.get('/api/users/' + id)
        assert rv.status_code == 404

    def test_error_post_empty_body(self):
        rv = self.client.post('/api/users', data=json.dumps(
                              {}
                              ), follow_redirects=True)
        assert rv.status_code == 400

    def test_error_post_user_with_made_user(self):
        rv = self.create_user("test1")
        rv = self.client.post('/api/users/test1', data=json.dumps(
                              {'id': 'test-id'}
                              ), follow_redirects=True)
        assert rv.status_code == 405

    def test_error_put_user_with_id(self):
        """READONLY TEST"""
        rv = self.create_user("test1")
        rv = self.client.put('/api/users/test1', data=json.dumps(
                             {'id': 'test-id'}
                             ), follow_redirects=True)
        assert rv.status_code == 403

    def test_error_put_user_with_username(self):
        """READONLY TEST"""
        rv = self.create_user("test1")
        rv = self.client.put('/api/users/test1', data=json.dumps(
                             {'username': 'test-id'}
                             ), follow_redirects=True)
        assert rv.status_code == 403

    def test_error_delete_fail_user(self):
        rv = self.client.delete('/api/users/asfdf', follow_redirects=True)
        assert rv.status_code == 404
