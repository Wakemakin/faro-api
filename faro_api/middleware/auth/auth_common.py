import logging

logger = logging.getLogger('faro_api.' + __name__)


class AuthMiddlewareBase(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        logger.debug("Calling auth middleware")
        self.create_auth_context(environ)
        return self.app(environ, start_response)

    def create_auth_context(self, env):
        env['auth'] = {}
