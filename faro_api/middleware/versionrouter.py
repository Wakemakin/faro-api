import logging

logger = logging.getLogger('faro_api.' + __name__)


class VersionRouter(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
