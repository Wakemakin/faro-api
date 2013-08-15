import json
import logging
import unittest

import faro_api
from faro_common import utils as utils

logger = logging.getLogger("faro_api."+__name__)


class DataProviderTest(unittest.TestCase):

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

    def create_dataproviders_with_user(self, name, username='test_user'):
        self.create_user(username)
        return self.client.post('/dataproviders', data=json.dumps(
                                {'name': name,
                                 'owner_id': username}
                                ), follow_redirects=True)

    def test_delete_user_with_dataprovider(self):
        rv = self.create_dataproviders_with_user("provider")
        rv = self.client.delete('/users/test_user',
                                follow_redirects=True)
        self.assertEqual(rv.status_code, 204)
        rv = self.client.get('/dataproviders')
        res = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(res['objects'], [])

    def test_get_empty_dataproviders(self):
        rv = self.client.get('/dataproviders')
        res = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(res['objects'], [])

    def test_get_dataproviders_under_user(self):
        self.create_user("john")
        rv = self.client.get('/users/john/dataproviders')
        self.assertEqual(rv.status_code, 200)

    def test_post_dataproviders(self):
        self.create_user("john")
        rv = self.client.post('/dataproviders', data=json.dumps(
                              {'name': "test provider",
                               'owner_id': 'john'}
                              ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertEqual(rv.status_code, 201)
        self.assertTrue(utils.is_uuid(res['id']))

    def test_put_dataproviders_rename(self):
        rv = self.create_dataproviders_with_user("test provider")
        self.assertEqual(rv.status_code, 201)
        res = json.loads(rv.data)
        self.assertEqual(res['name'], 'test provider')
        id = res['id']
        rv = self.client.put('/dataproviders/' + id, data=json.dumps(
                             {'name': "renamed"}
                             ), follow_redirects=True)
        res = json.loads(rv.data)
        self.assertEqual(res['name'], 'renamed')

    def test_delete_dataproviders(self):
        rv = self.create_dataproviders_with_user("test provider")
        res = json.loads(rv.data)
        id = res['id']
        rv = self.client.delete('/dataproviders/'+id,
                                follow_redirects=True)
        self.assertEqual(rv.status_code, 204)
