from flask import Flask

from faro_api.utils import make_json_app


app = make_json_app(Flask(__name__))
app.config.from_object('apiconfig')


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()

from faro_api.views import endpoint
from faro_api.views import users
from faro_api.views import events
app.register_blueprint(endpoint.mod)
app.register_blueprint(users.mod)
app.register_blueprint(events.mod)

from faro_api.database import db_session
