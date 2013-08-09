import flask
import logging
import sys

import faro_api.database as db
import faro_api.utils as utils
import faro_common.decorators as dec
import faro_common.flask as flaskutils


class MyFlask(flask.Flask):
    pass

logger = logging.getLogger('faro_api')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

ch.setFormatter(formatter)
logger.addHandler(ch)


@dec.static_var("instance", None)
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
        auth_module = app.instance.config['AUTH_STRATEGY']
        auth_middleware = utils.load_constructor_from_string(auth_module)
        if auth_middleware is None:
            logger.fatal("Could not load middleware from %s" % auth_module)
            exit(1)

        try:
            app.instance.config.from_envvar('FARO_SETTINGS')
        except RuntimeError:
            pass
        app.instance.wsgi_app = auth_middleware(app.instance.wsgi_app)
    return app.instance
