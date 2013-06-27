import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'faro-api.db')
DATABASE_CONNECT_OPTIONS = {}

del os
