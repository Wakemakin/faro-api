import json
import logging
import unittest

import faro_api
from faro_common import utils

logger = logging.getLogger("faro_api."+__name__)


class QuestionTest(unittest.TestCase):

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

    def create_event_with_user(self, name, username='test_user'):
        self.create_user(username)
        return self.client.post('/events', data=json.dumps(
                                {'name': name,
                                 'owner_id': username}
                                ), follow_redirects=True)

    def create_question_with_user(self, name, username='test_user'):
        self.create_user(username)
        return self.client.post('/questions', data=json.dumps(
                                {'name': name,
                                 'owner_id': username}
                                ), follow_redirects=True)

    def test_regression_delete_user_with_questions(self):
        rv = self.create_user("john")
        res = json.loads(rv.data)
        user_id = res['id']
        uri = "/users/%s/questions" % user_id
        rv = self.client.post(uri, data=json.dumps(
                              {'name': 'test'}), follow_redirects=True)
        self.assertEqual(rv.status_code, 201)
        rv = self.client.delete("/users/john", follow_redirects=True)
        self.assertEqual(rv.status_code, 204)

    def test_postget_question_under_user(self):
        rv = self.create_user("john")
        res = json.loads(rv.data)
        user_id = res['id']
        uri = "/users/%s/questions" % user_id
        rv = self.client.post(uri, data=json.dumps(
                              {'name': 'test'}), follow_redirects=True)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertEqual(rv.status_code, 201)
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))
        rv = self.client.get(uri)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertTrue(len(res['objects']) == 1)

    def test_postget_question_under_user_with_event(self):
        rv = self.create_event_with_user("event", username="john")
        res = json.loads(rv.data)
        event_id = res['id']
        uri = "/users/john/questions"
        rv = self.client.post(uri, data=json.dumps(
                              {'name': 'test',
                               'event_id': event_id}),
                              follow_redirects=True)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertEqual(rv.status_code, 201)
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))
        rv = self.client.get(uri)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertTrue(len(res['objects']) == 1)

    def test_postget_question_under_event(self):
        rv = self.create_event_with_user("event")
        res = json.loads(rv.data)
        event_id = res['id']
        uri = "/events/%s/questions" % event_id
        rv = self.client.post(uri, data=json.dumps(
                              {'name': 'test',
                               'owner_id': 'test_user'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertEqual(rv.status_code, 201)
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))
        rv = self.client.get(uri)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertTrue(len(res['objects']) == 1)

    def test_postget_question_under_event_no_user_given(self):
        rv = self.create_event_with_user("event")
        res = json.loads(rv.data)
        event_id = res['id']
        uri = "/events/%s/questions" % event_id
        rv = self.client.post(uri, data=json.dumps(
                              {'name': 'test'}), follow_redirects=True)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertEqual(rv.status_code, 201)

    def test_move_question_between_users(self):
        rv = self.create_user("john")
        res = json.loads(rv.data)
        user_id = res['id']
        rv = self.create_question_with_user("q1")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.put('/questions/'+id, data=json.dumps(
                             {'owner_id': 'john'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertTrue(res['owner_id'] == user_id)
        self.assertEqual(rv.status_code, 200)

    def test_get_empty_questions(self):
        rv = self.client.get('/questions')
        res = json.loads(rv.data)
        self.assertTrue(res['objects'] == [])
        self.assertEqual(rv.status_code, 200)

    def test_get_one_question(self):
        rv = self.create_question_with_user("test")
        rv = self.client.get('/questions')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 1)

    def test_get_one_question_by_id(self):
        rv = self.create_question_with_user("test")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.get('/questions/' + id)
        res = json.loads(rv.data)
        self.assertTrue(res['object']['name'] == 'test')
        self.assertTrue(res['object']['id'] == id)

    def test_get_multi_question(self):
        rv = self.create_question_with_user("test1")
        rv = self.create_question_with_user("test2")
        rv = self.client.get('/questions')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 2)

    def test_post_question_just_name(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/questions', data=json.dumps(
                              {'name': 'test',
                               'owner_id': 'test_user'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        logger.debug(rv.data)
        self.assertEqual(rv.status_code, 201)
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))

    def test_post_question(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/questions', data=json.dumps(
                              {'name': 'test',
                               'description': 'derp',
                               'owner_id': 'test_user'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(res['name'] == 'test')
        self.assertTrue(res['id'] is not None)
        self.assertTrue(utils.is_uuid(res['id']))
        self.assertEqual(rv.status_code, 201)

    def test_post_question_with_id(self):
        """Should this test fail?"""
        rv = self.create_user('test_user')
        rv = self.client.post('/questions', data=json.dumps(
                              {'name': 'test',
                               'id': 'test-id',
                               'description': 'derp',
                               'owner_id': 'test_user'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(res['id'] != 'test-id')
        self.assertEqual(rv.status_code, 201)

    def test_put_question_with_name(self):
        rv = self.create_question_with_user('test_question')
        res = json.loads(rv.data)
        id = res['id']
        self.assertTrue(res['name'] == 'test_question')
        rv = self.client.put('/questions/'+id, data=json.dumps(
                             {'name': 'test'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(res['name'] == 'test')
        self.assertEqual(rv.status_code, 200)

    def test_filter_question_by_owner(self):
        rv = self.create_question_with_user("test", "derp")
        rv = self.create_question_with_user("test2", "herp")
        rv = self.client.get('/questions')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 2)
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get('/questions?owner_id=derp')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 1)
        self.assertEqual(rv.status_code, 200)

    def test_put_question_with_description(self):
        rv = self.create_question_with_user('test_question')
        res = json.loads(rv.data)
        id = res['id']
        self.assertTrue(res['description'] is None)
        rv = self.client.put('/questions/'+id, data=json.dumps(
                             {'description': 'test'}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertTrue(res['description'] == 'test')
        self.assertEqual(rv.status_code, 200)

    def test_filter_question_by_name(self):
        rv = self.create_question_with_user("test", "asdf")
        rv = self.create_question_with_user("derp", "asdf2")
        rv = self.client.get('/questions')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 2)
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get('/questions?name=derp')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 1)
        self.assertEqual(rv.status_code, 200)

    def test_delete_question(self):
        rv = self.create_question_with_user("test")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.delete('/questions/'+id, follow_redirects=True)
        self.assertEqual(rv.status_code, 204)

    def test_error_get_question_by_fail_user(self):
        id = str(utils.make_uuid())
        rv = self.client.get('/users/'+id+'/questions')
        self.assertEqual(rv.status_code, 404)

    def test_error_get_one_question_by_fail_id(self):
        id = str(utils.make_uuid())
        rv = self.client.get('/questions/'+id)
        self.assertEqual(rv.status_code, 404)

    def test_error_post_question_empty_body(self):
        rv = self.client.post('/questions', data=json.dumps(
                              {}
                              ), follow_redirects=True)
        self.assertEqual(rv.status_code, 400)

    def test_error_post_question_no_user(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/questions', data=json.dumps(
                              {'description': 'herps and derps'}),
                              follow_redirects=True)
        self.assertEqual(rv.status_code, 409)

    def test_error_post_question_fail_event(self):
        id = str(utils.make_uuid())
        rv = self.create_user('test_user')
        uri = "/events/%s/questions" % id
        rv = self.client.post(uri, data=json.dumps(
                              {'description': 'herps and derps',
                               'owner_id': 'test_user'}
                              ), follow_redirects=True)
        self.assertEqual(rv.status_code, 404)

    def test_error_post_question_fail_user(self):
        id = str(utils.make_uuid())
        uri = "/users/%s/questions" % id
        rv = self.client.post(uri, data=json.dumps(
                              {'description': 'herps and derps'}),
                              follow_redirects=True)
        self.assertEqual(rv.status_code, 404)

    def test_error_post_question_no_name(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/questions', data=json.dumps(
                              {'description': 'herps and derps',
                               'owner_id': 'test_user'}
                              ), follow_redirects=True)
        self.assertEqual(rv.status_code, 409)

    def test_error_post_question_with_made_question(self):
        rv = self.create_user('test_user')
        rv = self.create_question_with_user("test")
        id = json.loads(rv.data)['id']
        rv = self.client.post('/questions/'+id, data=json.dumps(
                              {'name': 'test',
                               'owner_id': 'test_user'}
                              ), follow_redirects=True)
        self.assertEqual(rv.status_code, 405)

    def test_error_put_question_with_id(self):
        rv = self.create_question_with_user("test")
        id = json.loads(rv.data)['id']
        rv = self.client.put('/questions/'+id, data=json.dumps(
                             {'id': 'test'}
                             ), follow_redirects=True)
        self.assertEqual(rv.status_code, 403)

    def test_error_put_question_with_no_body(self):
        rv = self.create_question_with_user("test")
        id = json.loads(rv.data)['id']
        rv = self.client.put('/questions/'+id, data=json.dumps(
                             {}), follow_redirects=True)
        self.assertEqual(rv.status_code, 400)

    def test_error_delete_fail_question(self):
        id = str(utils.make_uuid())
        rv = self.client.delete('/questions/'+id)
        self.assertEqual(rv.status_code, 404)
