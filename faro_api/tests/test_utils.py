import logging
import unittest

from faro_api import utils

logger = logging.getLogger('faro_api.'+__name__)


class UtilTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generate_temp_database(self):
        """Ensure that the file names created are unique each time."""
        filenames = set([utils.generate_temp_database() for i in range(100)])
        self.assertTrue(len(filenames) == 100)

    def test_load_constructor_from_string_erroneously(self):
        self.assertIsNone(utils.load_constructor_from_string("derp"))
        self.assertIsNone(utils.load_constructor_from_string("derp.derp"))
        self.assertIsNone(utils.load_constructor_from_string("derp.."))
        self.assertIsNone(utils.load_constructor_from_string(None))
        self.assertIsNone(utils.load_constructor_from_string(""))
        self.assertIsNone(utils.load_constructor_from_string({}))
        pkg = 'faro_api.middleware.auth.noauth.NoAuthMiddlewar'
        self.assertIsNone(utils.load_constructor_from_string(pkg))

    def test_load_constructor_from_string(self):
        pkg = 'faro_api.middleware.auth.noauth.NoAuthMiddleware'
        self.assertIsNotNone(utils.load_constructor_from_string(pkg))
