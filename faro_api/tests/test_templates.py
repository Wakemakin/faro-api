import json
import logging
import unittest

import faro_api

logger = logging.getLogger("faro_api."+__name__)


class TemplateTest(unittest.TestCase):

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

    def create_template(self, title, type):
        return self.client.post('/templates', data=json.dumps(
                                {'title': title, 'template_type': type}
                                ), follow_redirects=True)

    def test_get_empty_templates(self):
        rv = self.client.get('/templates')
        res = json.loads(rv.data)
        assert res['objects'] == []
        assert rv.status_code == 200

    def test_get_multiple_templates(self):
        self.create_template('test', 'list')
        self.create_template('test', 'list')
        rv = self.client.get('/templates')
        res = json.loads(rv.data)
        assert len(res['objects']) == 2
        assert rv.status_code == 200

    def test_get_template_under_owner(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/users/test_user/templates',
                              data=json.dumps({'title': "title",
                                               'template_type': "list"}),
                              follow_redirects=True)
        rv = self.client.get('/users/test_user/templates',
                             follow_redirects=True)
        res = json.loads(rv.data)
        assert len(res['objects']) == 1
        assert rv.status_code == 200

    def test_create_template_without_owner(self):
        rv = self.client.post('/templates', data=json.dumps(
                              {'title': "title", 'template_type': "list"}
                              ), follow_redirects=True)
        assert rv.status_code == 201
        res = json.loads(rv.data)
        assert res['title'] == "title"

    def test_create_template_with_owner(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/templates', data=json.dumps(
                              {'title': "title",
                               'owner_id': 'test_user',
                               'template_type': "list"}
                              ), follow_redirects=True)
        assert rv.status_code == 201
        res = json.loads(rv.data)
        assert res['title'] == "title"
        assert res['owner'] is not None
        assert res['owner']['username'] == 'test_user'

    def test_create_template_under_owner(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/users/test_user/templates',
                              data=json.dumps({'title': "title",
                                               'template_type': "list"}),
                              follow_redirects=True)
        assert rv.status_code == 201
        res = json.loads(rv.data)
        assert res['title'] == "title"
        assert res['owner'] is not None
        assert res['owner']['username'] == 'test_user'

    def test_update_template_title(self):
        rv = self.create_template("name", "list")
        res = json.loads(rv.data)
        assert 'id' in res
        template_id = res['id']
        assert 'title' in res
        assert res['title'] == 'name'
        rv = self.client.put('/templates/%s' % template_id,
                             data=json.dumps({'title': "new title"}),
                             follow_redirects=True)
        res = json.loads(rv.data)
        assert 'id' in res
        assert res['id'] == template_id
        assert 'title' in res
        assert res['title'] == 'new title'

    def test_update_template_description(self):
        rv = self.create_template("name", "list")
        res = json.loads(rv.data)
        assert 'id' in res
        template_id = res['id']
        assert 'description' in res
        assert res['description'] is None
        rv = self.client.put('/templates/%s' % template_id,
                             data=json.dumps({'description': "desc"}),
                             follow_redirects=True)
        res = json.loads(rv.data)
        assert 'id' in res
        assert res['id'] == template_id
        assert 'description' in res
        assert res['description'] == 'desc'

    def test_error_create_template_without_title(self):
        rv = self.client.post('/templates', data=json.dumps(
                              {'template_type': "list"}
                              ), follow_redirects=True)
        assert rv.status_code == 400

    def test_error_create_template_without_type(self):
        rv = self.client.post('/templates', data=json.dumps(
                              {'title': "title"}
                              ), follow_redirects=True)
        assert rv.status_code == 400

    def test_error_create_template_under_bad_owner(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/users/herpderp/templates',
                              data=json.dumps({'title': "title",
                                               'template_type': "list"}),
                              follow_redirects=True)
        assert rv.status_code == 404

    def test_error_create_template_with_bad_owner(self):
        rv = self.create_user('test_user')
        rv = self.client.post('/templates', data=json.dumps(
                              {'title': "title", 'owner_id': 'hper_derp',
                               'template_type': "list"}
                              ), follow_redirects=True)
        assert rv.status_code == 404

    def test_error_update_template_type(self):
        rv = self.create_template("name", "list")
        res = json.loads(rv.data)
        assert 'id' in res
        template_id = res['id']
        rv = self.client.put('/templates/%s' % template_id,
                             data=json.dumps({'template_type': "desc"}),
                             follow_redirects=True)
        assert rv.status_code == 403
