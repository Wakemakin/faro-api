import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_FILE = 'faro.db'


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_CONNECT_OPTIONS = {}
    DEFAULT_PAGE_SIZE = 15
    MAXIMUM_PAGE_SIZE = 100

    """PAGINATION CONSTANTS"""
    PAGE_QUERY = 'p'
    PAGE_SIZE_QUERY = 'page_size'
    PAGE_TOTAL_QUERY = 'total'
    PAGE_NUMBER_QUERY = 'page_number'
    PAGE_NEXT = 'next'
    PAGE_PREVIOUS = 'prev'


class DevelopmentConfig(Config):
    import os
    _basedir = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, DATABASE_FILE)
    del os


class TestConfig(Config):
    DEBUG = True
    TESTING = True
