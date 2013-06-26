from utils import common
from db.database import init_db

from api import api
from api import v1 as v1_api
from api.v1 import event

app = common.make_json_app(__name__)
app.config['DEBUG'] = True


if __name__ == "__main__":
    app.db = init_db()
    api_endpoint = api.FaroEndpoint(app, 'api')
    v1 = v1_api.Version1Endpoint(app)
    event = event.Events(app)
    v1.add_child(event)
    api_endpoint.add_child(v1)
    api_endpoint.register()

    app.run(host='0.0.0.0', port=5002)
