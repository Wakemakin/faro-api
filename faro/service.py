import flask
import flask.ext.sqlalchemy
import flask.ext.restless

from db import models as db
from utils import common


app = common.make_json_app(__name__)
app.config['DEBUG'] = True

mysession = db.make_session()

manager = flask.ext.restless.APIManager(app, session=mysession)

manager.create_api(db.User, methods=['GET', 'POST', 'DELETE'])
manager.create_api(db.Event, methods=['GET', 'POST', 'DELETE'])
manager.create_api(db.Choice, methods=['GET', 'POST', 'DELETE'])

app.run(host='0.0.0.0', port=5001)
