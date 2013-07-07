import unittest
import logging
import json

import faro_api

logger = logging.getLogger("faro-api."+__name__)


class PageTest(unittest.TestCase):

    def setUp(self):
        self.app = faro_api.app(testing=True)
        self.client = self.app.test_client()
        self.page_size = self.app.config['DEFAULT_PAGE_SIZE']
        self.pages = 10
        self.remainder = self.page_size / 2

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def create_user(self, name):
        return self.client.post('/api/users', data=json.dumps(
                                {'username': name}
                                ), follow_redirects=True)

    def test_get_lots_of_users_default_paging(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == self.page_size
        for x in range(self.page_size):
            assert res['objects'][x]['username'] == str(x)
        assert res['total'] == total
        assert res['page_number'] == 1
        assert 'next' in res
        assert res['next'] == 'http://localhost/api/users?p=2'
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_lots_of_users_default_pageltzero(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/api/users?p=-2')
        res = json.loads(rv.data)
        assert len(res['objects']) == self.page_size
        for x in range(self.page_size):
            assert res['objects'][x]['username'] == str(x)
        assert res['total'] == total
        assert res['page_number'] == 1
        assert 'next' in res
        assert res['next'] == 'http://localhost/api/users?p=2'
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_lots_of_users_default_pagezero(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/api/users?p=0')
        res = json.loads(rv.data)
        assert len(res['objects']) == self.page_size
        for x in range(self.page_size):
            assert res['objects'][x]['username'] == str(x)
        assert res['total'] == total
        assert res['page_number'] == 1
        assert 'next' in res
        assert res['next'] == 'http://localhost/api/users?p=2'
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_lots_of_users_default_page1(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/api/users?p=1')
        res = json.loads(rv.data)
        assert len(res['objects']) == self.page_size
        for x in range(self.page_size):
            assert res['objects'][x]['username'] == str(x)
        assert res['total'] == total
        assert res['page_number'] == 1
        assert 'next' in res
        assert res['next'] == 'http://localhost/api/users?p=2'
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_lots_of_users_default_page2(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/api/users?p=2')
        res = json.loads(rv.data)
        for x in range(self.page_size):
            assert res['objects'][x]['username'] == str(x+self.page_size)
        assert res['total'] == total
        assert res['page_number'] == 2
        assert 'next' in res
        assert res['next'] == 'http://localhost/api/users?p=3'
        assert 'prev' in res
        assert res['prev'] == 'http://localhost/api/users?p=1'
        assert res['page_size'] == self.page_size

    def test_iterate_using_next(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/api/users')
        res = json.loads(rv.data)
        while 'next' in res:
            next_url = res['next']
            next_url = next_url.replace('http://localhost', '')
            rv = self.client.get(next_url)
            res = json.loads(rv.data)
        assert res['page_number'] == self.pages + 1
        last = str(total - 1)
        last_username = res['objects'][len(res['objects'])-1]['username']
        logger.debug("%s, %s" % (last, last_username))
        assert last_username == last
