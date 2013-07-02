import unittest
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from faro_api import app
from faro_api import database as db

logger = logging.getLogger(__name__)


class UserTest(unittest.TestCase):

    def setUp(self):
        engine = create_engine("sqlite:////tmp/tmp.db", echo=True,
                               convert_unicode=True)
        db.db_session = scoped_session(sessionmaker(autocommit=False,
                                                    autoflush=False,
                                                    bind=engine))
        self.app = app.test_client()
        db.init_db(engine=engine)

    def test_empty_users(self):
        rv = self.app.get('/api/users')
        logger.debug(rv.data)
        assert False

    def tearDown(self):
        pass

    def test_pass(self):
        assert True

    def test_fail(self):
        assert False
