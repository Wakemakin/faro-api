import os
import ConfigParser

_basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_FILE = 'faro.db'


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_CONNECT_OPTIONS = {}
    DEFAULT_PAGE_SIZE = 15
    MAXIMUM_PAGE_SIZE = 100
    AUTH_STRATEGY = 'faro_api.middleware.auth.noauth.NoAuthMiddleware'

    """PAGINATION CONSTANTS"""
    PAGE_QUERY = 'p'
    PAGE_SIZE_QUERY = 'page_size'
    PAGE_TOTAL_QUERY = 'total'
    PAGE_NUMBER_QUERY = 'page_number'
    PAGE_NEXT = 'next'
    PAGE_PREVIOUS = 'prev'


class DevelopmentConfig(Config):
    db_user = 'root'
    db_password = 'password'
    db_host = 'localhost'
    db_name = 'faro_api'
    try:
        with open('/etc/faro-api/faro-api.conf'):
            config = ConfigParser.SafeConfigParser(
                {'db_user': db_user, 'db_password': db_password,
                 'db_host': db_host, 'db_name': db_name})
            config.read('/etc/faro-api/faro-api.conf')
            db_user = config.get('faro_api', 'db_user')
            db_password = config.get('faro_api', 'db_password')
            db_host = config.get('faro_api', 'db_host')
            db_name = config.get('faro_api', 'db_name')
    except IOError:
        pass
    uri = "mysql://%s:%s@%s/%s" % (db_user, db_password, db_host, db_name)
    DATABASE_URI = uri


class TestConfig(Config):
    DEBUG = True
    AUTH_STRATEGY = 'faro_api.middleware.auth.noauth.AdminAuthMiddleware'
    TESTING = True
