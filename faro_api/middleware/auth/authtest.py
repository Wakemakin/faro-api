import datetime
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
