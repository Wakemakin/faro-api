import logging
import unittest

import faro_api

logger = logging.getLogger("faro_api."+__name__)


class LoginTokenTest(unittest.TestCase):

    def setUp(self):
        auth = "faro_api.middleware.auth.authtest.TestNoAuth"
        self.app = faro_api.app(testing=True, auth_strategy=auth)
        self.client = self.app.test_client()

    def tearDown(self):
        import os
        os.remove(self.app.config['DATABASE_FILE'])
        del os

    def test_get_tokens(self):
        rv = self.client.get('/tokens')
        self.assertEquals(405, rv.status_code)
