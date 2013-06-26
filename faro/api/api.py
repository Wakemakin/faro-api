import common as api


class FaroEndpoint(api.ApiEndpoint):
    def __init__(self, app, name, prefix=None):
        super(FaroEndpoint, self).__init__(app, prefix=prefix, name=name)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            app.db.remove()
