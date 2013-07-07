import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_FILE = 'faro.db'


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_CONNECT_OPTIONS = {}
    DEFAULT_PAGE_SIZE = 15


class DevelopmentConfig(Config):
    import os
    _basedir = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, DATABASE_FILE)
    del os


class TestConfig(Config):
    DEBUG = True
    TESTING = True
