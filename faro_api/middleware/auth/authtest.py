import datetime
import werkzeug.wrappers as wz

import faro_api.middleware.auth.noauth as auth


class TestAdminAuth(auth.NoAuthMiddleware):

    def __init__(self, app):
        super(TestAdminAuth, self).__init__(app)

    def create_auth_context(self, env):
        super(TestAdminAuth, self).create_auth_context(env)
        env['auth']['userid'] = 0
        env['auth']['is_admin'] = True
        futuredate = datetime.date.today() + datetime.timedelta(365)
        env['auth']['valid_until'] = futuredate.isoformat()


class TestNoAuth(auth.NoAuthMiddleware):

    def __init__(self, app):
        super(TestNoAuth, self).__init__(app)

    def create_auth_context(self, env):
        super(TestNoAuth, self).create_auth_context(env)
        env['auth']['userid'] = 0
        env['auth']['is_admin'] = False
        futuredate = datetime.date.today() + datetime.timedelta(365)
        env['auth']['valid_until'] = futuredate.isoformat()


class TestExpiredAuth(auth.NoAuthMiddleware):

    def __init__(self, app):
        super(TestExpiredAuth, self).__init__(app)

    def create_auth_context(self, env):
        super(TestExpiredAuth, self).create_auth_context(env)
        env['auth']['userid'] = 0
        env['auth']['is_admin'] = True
        futuredate = datetime.date.today() + datetime.timedelta(-1)
        env['auth']['valid_until'] = futuredate.isoformat()


class TestTogglingAuth(auth.NoAuthMiddleware):

    def __init__(self, app):
        super(TestTogglingAuth, self).__init__(app)

    def create_auth_context(self, env):
        super(TestTogglingAuth, self).create_auth_context(env)
        request = wz.Request(env)

        uid = request.headers.get('X-Auth-Id', None)
        env['auth']['userid'] = 0
        if uid is not None:
            env['auth']['userid'] = uid

        token = request.headers.get('X-Auth-Token', None)
        env['auth']['is_admin'] = False
        if token == 'ABC123':
            env['auth']['is_admin'] = True

        futuredate = datetime.date.today() + datetime.timedelta(365)
        env['auth']['valid_until'] = futuredate.isoformat()
