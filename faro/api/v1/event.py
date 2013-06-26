from flask import abort, jsonify, request
import api.common as api


RESOURCE = "event"
RESOURCE_COLLECTION = "events"
class Events(api.ResourceEndpoint):

    def _make_event_dict(self, event):
        return {}

    def __init__(self, app):
        super(Events, self).__init__(app, RESOURCE, RESOURCE_COLLECTION)

    def define_routes(self):
        super(Events, self).define_routes()
        endpoint = self.endpoint()

        @endpoint.route('/', methods=['GET', 'POST'])
        def show():
            if request.method == 'POST':
                abort(500)
            elif request.method == 'GET':
                try:
                    return jsonify(events=[])
                except:
                    abort(500)

    def make_blueprint(self):
        super(Events, self).make_blueprint(False)
