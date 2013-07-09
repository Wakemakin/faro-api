import logging
import unittest
import uuid

from faro_api import utils

logger = logging.getLogger('faro_api.'+__name__)


class UserTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generate_temp_database(self):
        """Ensure that the file names created are unique each time."""
        filenames = set([utils.generate_temp_database() for i in range(100)])
        assert len(filenames) == 100

    def test_static_var_decorator(self):
        """Ensure that static variables in functions are carried over."""
        @utils.static_var("c", 0)
        def counting_function():
            counting_function.c += 1
            return counting_function.c
        assert counting_function() == 1
        assert counting_function() == 2
        assert counting_function() == 3
        assert counting_function() == 4

    def test_make_uuid(self):
        temp_uuid = utils.make_uuid()
        assert isinstance(temp_uuid, uuid.UUID)
        assert len(str(temp_uuid)) == 36

    def test_make_uuid_uniqueness(self):
        uuids = set([utils.make_uuid() for i in range(100)])
        assert len(uuids) == 100

    def test_uuid_check_valid(self):
        uuids = set([utils.make_uuid() for i in range(100)])
        for uuid in uuids:
            assert utils.is_uuid(uuid)

    def test_uuid_check_invalid(self):
        assert not utils.is_uuid("asdf")
        assert not utils.is_uuid("")
        assert not utils.is_uuid(None)
