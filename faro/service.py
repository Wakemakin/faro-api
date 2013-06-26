from utils import common
from db.database import init_db

from api import api

app = common.make_json_app(__name__)
app.config['DEBUG'] = True
app.register_blueprint(api.api_endpoint)


if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0')
