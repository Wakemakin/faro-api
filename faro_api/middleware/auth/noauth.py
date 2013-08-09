import datetime
import faro_api.middleware.auth.auth_common as auth


class NoAuthMiddleware(auth.AuthMiddlewareBase):

    def __init__(self, app):
        super(NoAuthMiddleware, self).__init__(app)

    def create_auth_context(self, env):
        super(NoAuthMiddleware, self).create_auth_context(env)
        env['auth']['userid'] = 0
        env['auth']['is_admin'] = False
        futuredate = datetime.date.today() + datetime.timedelta(365)
        env['auth']['valid_until'] = futuredate.isoformat()


class AdminAuthMiddleware(NoAuthMiddleware):

    def __init__(self, app):
        super(NoAuthMiddleware, self).__init__(app)

    def create_auth_context(self, env):
        super(NoAuthMiddleware, self).create_auth_context(env)
        env['auth']['userid'] = 0
        env['auth']['is_admin'] = True
        futuredate = datetime.date.today() + datetime.timedelta(365)
        env['auth']['valid_until'] = futuredate.isoformat()
