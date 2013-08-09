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
