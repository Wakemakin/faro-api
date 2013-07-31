import flask

import faro_api.database as db
import faro_api.utils as utils

import faro_common.flask as flaskutils


class MyFlask(flask.Flask):
    pass


@utils.static_var("instance", None)
def app(testing=False, create_db=False):
    if testing or app.instance is None:
        app.instance = flaskutils.make_json_app(MyFlask(__name__))
        config = 'apiconfig.DevelopmentConfig'
        if testing:
            config = 'apiconfig.TestConfig'
            app.instance.config['DATABASE_FILE'] = utils.\
                generate_temp_database()
            uri = 'sqlite:///' + app.instance.config['DATABASE_FILE']
            app.instance.config['DATABASE_URI'] = uri
        app.instance.config.from_object(config)
        session = db.create_db_environment(app.instance)
        if create_db:
            return True

        @app.instance.before_request
        def before_request():
            flask.g.session = session

        from faro_api.views import dataproviders
        from faro_api.views import endpoint
        from faro_api.views import events
        from faro_api.views import questions
        from faro_api.views import users
        app.instance.register_blueprint(endpoint.mod)
        user_bp = users.UserApi()
        event_bp = events.EventApi()
        question_bp = questions.QuestionApi()
        dps_bp = dataproviders.DataProviderApi()
        app.instance.register_blueprint(user_bp.blueprint)
        app.instance.register_blueprint(event_bp.blueprint)
        app.instance.register_blueprint(question_bp.blueprint)
        app.instance.register_blueprint(dps_bp.blueprint)

        try:
            app.instance.config.from_envvar('FARO_SETTINGS')
        except RuntimeError:
            pass
    return app.instance
