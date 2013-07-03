from flask import Flask, g

import faro_api.utils as utils
import faro_api.database as db


@utils.static_var("instance", None)
def app(testing=False):
    if testing or app.instance is None:
        app.instance = utils.make_json_app(Flask(__name__))
        config = 'apiconfig.DevelopmentConfig'
        if testing:
            config = 'apiconfig.TestConfig'
            app.instance.config['DATABASE_FILE'] = utils.\
                generate_temp_database()
            uri = 'sqlite:///' + app.instance.config['DATABASE_FILE']
            app.instance.config['DATABASE_URI'] = uri
        app.instance.config.from_object(config)
        session = db.create_db_environment(app.instance)

        @app.instance.before_request
        def before_request():
            g.session = session

        from faro_api.views import endpoint
        from faro_api.views import users
        from faro_api.views import events
        app.instance.register_blueprint(endpoint.mod)
        user_bp = users.UserApi()
        event_bp = events.EventApi()
        app.instance.register_blueprint(user_bp.blueprint)
        app.instance.register_blueprint(event_bp.blueprint)

        try:
            app.instance.config.from_envvar('FARO_SETTINGS')
        except RuntimeError:
            pass
    return app.instance
