import json
import logging
import unittest

import faro_api

logger = logging.getLogger('faro_api.'+__name__)


class PageTest(unittest.TestCase):

    def setUp(self):
        self.app = faro_api.app(testing=True)
        self.client = self.app.test_client()
        self.page_size = self.app.config['DEFAULT_PAGE_SIZE']
        self.small_page_size = 5
        self.medium_page_size = 10
        self.large_page_size = 50
        self.maximum_page_size = self.app.config['MAXIMUM_PAGE_SIZE']
        self.total = self.large_page_size
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

    def test_get_no_users_default_max(self):
        rv = self.client.get('/users')
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == 0)
        self.assertTrue(res[self.tq] == 0)
        self.assertTrue(res[self.pnq] == 1)
        self.assertTrue(self.pnext not in res)
        self.assertTrue(self.pprev not in res)
        self.assertTrue(self.psq in res)
        self.assertTrue(res[self.psq] == self.page_size)

    def test_get_min_users_small_page(self):
        page_size = self.small_page_size
        [self.create_user(str(x)) for x in range(self.total)]
        rv = self.client.get('/users?%s=%s' %
                             (self.psq, page_size))
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == page_size)
        self.assertTrue(res[self.tq] == self.total)
        self.assertTrue(res[self.pnq] == 1)
        self.assertTrue(self.pnext in res)
        self.assertTrue(('%s=2' % self.pq) in res[self.pnext])
        self.assertTrue(self.pprev not in res)
        self.assertTrue(self.psq in res)
        self.assertTrue(res[self.psq] == page_size)

    def test_get_min_users_medium_page(self):
        page_size = self.medium_page_size
        [self.create_user(str(x)) for x in range(self.total)]
        rv = self.client.get('/users?%s=%s' %
                             (self.psq, page_size))
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == page_size)
        self.assertTrue(res[self.tq] == self.total)
        self.assertTrue(res[self.pnq] == 1)
        self.assertTrue(self.pnext in res)
        self.assertTrue(('%s=2' % self.pq) in res[self.pnext])
        self.assertTrue(self.pprev not in res)
        self.assertTrue(self.psq in res)
        self.assertTrue(res[self.psq] == page_size)

    def test_get_min_users_large_page(self):
        page_size = self.large_page_size
        [self.create_user(str(x)) for x in range(self.total)]
        rv = self.client.get('/users?%s=%s' %
                             (self.psq, page_size))
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == page_size)
        self.assertTrue(res[self.tq] == self.total)
        self.assertTrue(res[self.pnq] == 1)
        self.assertTrue(self.pnext not in res)
        self.assertTrue(self.pprev not in res)
        self.assertTrue(self.psq in res)
        self.assertTrue(res[self.psq] == page_size)

    def test_get_min_users_too_big_page(self):
        true_page = self.maximum_page_size
        total = self.maximum_page_size * 2
        page_size = total
        [self.create_user(str(x)) for x in range(total)]
        rv = self.client.get('/users?%s=%s' %
                             (self.psq, page_size))
        res = json.loads(rv.data)
        self.assertTrue(len(res['objects']) == true_page)
        self.assertTrue(res[self.tq] == total)
        self.assertTrue(res[self.pnq] == 1)
        self.assertTrue(self.pnext in res)
        self.assertTrue(('%s=2' % self.pq) in res[self.pnext])
        self.assertTrue(self.pprev not in res)
        self.assertTrue(self.psq in res)
        self.assertTrue(res[self.psq] == true_page)

    def test_get_one_user_at_time(self):
        page_size = 1
        [self.create_user(str(x)) for x in range(self.total)]
        i = 0
        uri = '/users?%s=%s' % (self.psq, page_size)
        while i < self.total:
            rv = self.client.get(uri)
            res = json.loads(rv.data)
            if i < self.total - 1:
                self.assertTrue(self.pnext in res)
                self.assertTrue('p=%s' % (i+2) in res[self.pnext])
                self.assertTrue(('%s=%s' %
                                (self.pq, str(i+2))) in res[self.pnext])
                uri = res[self.pnext].replace('http://localhost', '')
            else:
                self.assertTrue(self.pnext not in res)
            if i > 0:
                self.assertTrue(self.pprev in res)
                self.assertTrue(('%s=%s' %
                                (self.pq, str(i))) in res[self.pprev])
            else:
                self.assertTrue(self.pprev not in res)
            self.assertTrue(len(res['objects']) == page_size)
            self.assertTrue(self.psq in res)
            self.assertTrue(res[self.psq] == page_size)
            i = i + 1
        self.assertTrue(i == self.total)
