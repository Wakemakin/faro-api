import json
import logging
import unittest

import faro_api

logger = logging.getLogger("faro_api."+__name__)


class PageTest(unittest.TestCase):

    def setUp(self):
        self.app = faro_api.app(testing=True)
        self.client = self.app.test_client()
        self.page_size = self.app.config['DEFAULT_PAGE_SIZE']
        self.pages = 5
        self.remainder = self.page_size / 2

        self.psq = self.app.config['PAGE_SIZE_QUERY']
        self.pq = self.app.config['PAGE_QUERY']
        self.tq = self.app.config['PAGE_TOTAL_QUERY']
        self.pnq = self.app.config['PAGE_NUMBER_QUERY']
        self.pnext = self.app.config['PAGE_NEXT']
        self.pprev = self.app.config['PAGE_PREVIOUS']

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def create_user(self, name):
        return self.client.post('/users', data=json.dumps(
                                {'username': name}
                                ), follow_redirects=True)

    def test_get_no_users_default_paging(self):
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == 0
        assert res['total'] == 0
        assert res['page_number'] == 1
        assert 'next' not in res
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_few_users_default_paging(self):
        total = self.page_size / 2
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == total
        assert res['total'] == total
        assert res['page_number'] == 1
        assert 'next' not in res
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_few_users_pageltzero(self):
        total = self.page_size / 2
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=-2')
        assert rv.status_code == 404

    def test_get_few_users_pagezero(self):
        total = self.page_size / 2
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=0')
        assert rv.status_code == 404

    def test_get_few_users_page1(self):
        total = self.page_size / 2
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=1')
        res = json.loads(rv.data)
        assert len(res['objects']) == total
        assert res['total'] == total
        assert res['page_number'] == 1
        assert 'next' not in res
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_lots_of_users_default_paging(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        assert len(res['objects']) == self.page_size
        for x in range(self.page_size):
            assert res['objects'][x]['username'] == str(x)
        assert res['total'] == total
        assert res['page_number'] == 1
        assert 'next' in res
        assert 'p=2' in res['next']
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_lots_of_users_default_pageltzero(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=-2')
        assert rv.status_code == 404

    def test_get_lots_of_users_page_too_far(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=%s' % str(self.pages + 2))
        assert rv.status_code == 404

    def test_get_lots_of_users_page_really_far(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=%s' % str(self.pages + 100000000))
        assert rv.status_code == 404

    def test_get_lots_of_users_default_pagezero(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=0')
        assert rv.status_code == 404

    def test_get_lots_of_users_default_page1(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=1')
        res = json.loads(rv.data)
        assert len(res['objects']) == self.page_size
        for x in range(self.page_size):
            assert res['objects'][x]['username'] == str(x)
        assert res['total'] == total
        assert res['page_number'] == 1
        assert 'next' in res
        assert 'p=2' in res['next']
        assert 'prev' not in res
        assert res['page_size'] == self.page_size

    def test_get_lots_of_users_default_page2(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?p=2')
        res = json.loads(rv.data)
        for x in range(self.page_size):
            assert res['objects'][x]['username'] == str(x+self.page_size)
        assert res['total'] == total
        assert res['page_number'] == 2
        assert 'next' in res
        assert 'p=3' in res['next']
        assert 'prev' in res
        assert 'p=1' in res['prev']
        assert res['page_size'] == self.page_size

    def test_iterate_using_next(self):
        total = self.page_size * self.pages + self.remainder
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users')
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
