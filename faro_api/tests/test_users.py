import json
import logging
import unittest

import faro_api
from faro_common import utils

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

    def test_get_empty_users(self):
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        self.assertTrue(res['objects'] == [])
        self.assertEqual(rv.status_code, 200)

    def test_get_one_user(self):
        rv = self.create_user("test2")
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 1)

    def test_get_one_user_by_username(self):
        rv = self.create_user("test")
        rv = self.client.get('/users/test')
        res = json.loads(rv.data)
        self.assertTrue(res['object']['username'] == 'test')

    def test_get_one_user_by_id(self):
        rv = self.create_user("test")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.get('/users/' + id)
        res = json.loads(rv.data)
        self.assertTrue(res['object']['username'] == 'test')
        self.assertTrue(res['object']['id'] == id)

    def test_get_multi_user(self):
        rv = self.create_user("test1")
        rv = self.create_user("test2")
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 2)

    def test_post_user_just_username(self):
        rv = self.client.post('/users', data=json.dumps(
                              {'username': 'test'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(res['username'] == 'test')
        self.assertTrue(res['first_name'] is None)
        self.assertTrue(res['last_name'] is None)
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))
        self.assertEqual(rv.status_code, 201)

    def test_post_user(self):
        rv = self.client.post('/users', data=json.dumps(
                              {'username': 'test',
                               'first_name': 'test-first',
                               'last_name': 'test-last'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(res['username'] == 'test')
        self.assertTrue(res['first_name'] == 'test-first')
        self.assertTrue(res['last_name'] == 'test-last')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))
        self.assertEqual(rv.status_code, 201)

    def test_post_user_with_id(self):
        """Should this test fail?"""
        rv = self.client.post('/users', data=json.dumps(
                              {'username': 'test',
                               'id': 'test-id'}
                              ), follow_redirects=True)
        self.assertEqual(rv.status_code, 201)

    def test_put_user_with_firstname(self):
        rv = self.create_user("test1")
        res = json.loads(rv.data)
        self.assertTrue(res['first_name'] is None)
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'first_name': 'new_name'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(res['first_name'] == 'new_name')
        self.assertEqual(rv.status_code, 200)

    def test_filter_user_no_results(self):
        rv = self.create_user("test1")
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 1)
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'first_name': 'test_name'}
                             ), follow_redirects=True)
        rv = self.client.get('/users?first_name=derp')
        res = json.loads(rv.data)
        self.assertTrue(res['objects'] == [])
        self.assertTrue(len(res['objects']) == 0)
        self.assertEqual(rv.status_code, 200)

    def test_filter_user_one_results(self):
        rv = self.create_user("test1")
        rv = self.create_user("test2")
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 2)
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'first_name': 'test_name'}
                             ), follow_redirects=True)
        rv = self.client.get('/users?first_name=test_name')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 1)
        self.assertEqual(rv.status_code, 200)

    def test_filter_user_two_results(self):
        rv = self.create_user("test1")
        rv = self.create_user("test2")
        rv = self.create_user("test3")
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 3)
        rv = self.client.put('/users/test2', data=json.dumps(
                             {'first_name': 'derp'}
                             ), follow_redirects=True)
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'first_name': 'derply'}
                             ), follow_redirects=True)
        rv = self.client.put('/users/test3', data=json.dumps(
                             {'first_name': 'hiyo'}
                             ), follow_redirects=True)
        rv = self.client.get('/users?first_name=derp')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 2)
        self.assertEqual(rv.status_code, 200)

    def test_filter_user_and_one_results(self):
        rv = self.create_user("test1")
        rv = self.create_user("test2")
        rv = self.create_user("test3")
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 3)
        rv = self.client.put('/users/test2', data=json.dumps(
                             {'first_name': 'derp',
                              'last_name': 'herp'}
                             ), follow_redirects=True)
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'first_name': 'derply',
                              'last_name': 'hiyo'}
                             ), follow_redirects=True)
        rv = self.client.put('/users/test3', data=json.dumps(
                             {'first_name': 'hiyo',
                              'last_name': 'herp'}
                             ), follow_redirects=True)
        rv = self.client.get('/users?first_name=derp&last_name=hi')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 1)
        self.assertEqual(rv.status_code, 200)

    def test_put_user_with_lastname(self):
        rv = self.create_user("test1")
        res = json.loads(rv.data)
        self.assertTrue(res['last_name'] is None)
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'last_name': 'new_name'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(res['last_name'] == 'new_name')
        self.assertEqual(rv.status_code, 200)

    def test_delete_user_by_id(self):
        rv = self.create_user("test1")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.delete('/users/'+id, follow_redirects=True)
        self.assertEqual(rv.status_code, 204)

    def test_delete_user_by_username(self):
        rv = self.create_user("test1")
        rv = self.client.delete('/users/test1', follow_redirects=True)
        self.assertEqual(rv.status_code, 204)

    def test_error_post_dupe_username(self):
        rv = self.create_user("test1")
        rv = self.create_user("test1")
        self.assertEqual(rv.status_code, 409)

    def test_error_get_one_user_by_fail_username(self):
        rv = self.client.get('/users/asdfasdf')
        self.assertEqual(rv.status_code, 404)

    def test_error_get_one_user_by_fail_id(self):
        id = str(utils.make_uuid())
        rv = self.client.get('/users/' + id)
        self.assertEqual(rv.status_code, 404)

    def test_error_post_empty_body(self):
        rv = self.client.post('/users', data=json.dumps(
                              {}
                              ), follow_redirects=True)
        self.assertEqual(rv.status_code, 400)

    def test_error_post_user_with_made_user(self):
        rv = self.create_user("test1")
        rv = self.client.post('/users/test1', data=json.dumps(
                              {'id': 'test-id'}
                              ), follow_redirects=True)
        self.assertEqual(rv.status_code, 405)

    def test_error_put_user_with_empty_data(self):
        rv = self.create_user("test1")
        rv = self.client.put('/users/test1', data=json.dumps(
                             {}
                             ), follow_redirects=True)
        self.assertEqual(rv.status_code, 400)

    def test_error_put_user_with_id(self):
        rv = self.create_user("test1")
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'id': 'test-id'}
                             ), follow_redirects=True)
        self.assertEqual(rv.status_code, 403)

    def test_error_put_bad_user(self):
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'username': 'test-id'}
                             ), follow_redirects=True)
        self.assertEqual(rv.status_code, 404)

    def test_error_put_user_with_username(self):
        rv = self.create_user("test1")
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'username': 'test-id'}
                             ), follow_redirects=True)
        self.assertEqual(rv.status_code, 403)

    def test_error_put_user_weird_column(self):
        rv = self.create_user("test1")
        rv = self.client.put('/users/test1', data=json.dumps(
                             {'bobbeh': 'something'}
                             ), follow_redirects=True)
        self.assertEqual(rv.status_code, 400)

    def test_error_post_user_weird_column(self):
        rv = self.client.post('/users', data=json.dumps(
                              {'username': 'test',
                               'bobbeh': 'something'}
                              ), follow_redirects=True)
        self.assertEqual(rv.status_code, 400)

    def test_error_delete_fail_user(self):
        rv = self.client.delete('/users/asfdf', follow_redirects=True)
        self.assertEqual(rv.status_code, 404)

    def test_regression_create_user_same_diff_caps(self):
        rv = self.create_user("roaet")
        rv = self.create_user("Roaet")
        self.assertEqual(rv.status_code, 409)

    def test_regression_get_user_same_diff_caps(self):
        rv = self.create_user("roaet")
        self.assertEqual(rv.status_code, 201)
        rv = self.client.get("/users/roaet")
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get("/users/Roaet")
        self.assertEqual(rv.status_code, 200)
