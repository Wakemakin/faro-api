from flask import Blueprint, abort, jsonify


class EndPoint(object):

    def __init__(self, app, prefix=None, name=None):
        self.children = list()
        self.app = app
        self.name = name
        self.session = app.db
        if prefix:
            self.prefix = "%s" % prefix
        else:
            self.prefix = None
        self.endpoint_name = self.__class__.__name__
        self.make_blueprint()

    def set_prefix(self, prefix):
        if prefix:
            self.prefix = "%s" % prefix
        self.make_blueprint()

    def append_prefix(self, prefix):
        if prefix:
            self.prefix = "%s/%s" % (prefix, self.prefix)
        self.make_blueprint()

    def create_index(self, endpoint):
        @endpoint.route('/')
        def show():
            try:
                children_index = []
                for child in self.children:
                    uri = "/%s" % child.prefix
                    children_index.append(uri)
                return jsonify(versions=children_index)
            except:
                abort(500)

    def make_blueprint(self, make_index=True):
        if self.prefix is not None:
            prefix = "/%s" % self.prefix
        else:
            prefix = "/"
        endpoint = Blueprint(self.name, self.endpoint_name,
                             url_prefix=prefix)

        if make_index:
            self.create_index(endpoint)
        self._endpoint = endpoint
        self.define_routes()
        return endpoint

    def define_routes(self):
        pass

    def endpoint(self):
        return self._endpoint

    def add_child(self, child_endpoint):
        self.children.append(child_endpoint)

    def register(self):
        self.app.register_blueprint(self.endpoint())
        print "Creating endpoint with prefix: %s" % self.endpoint().url_prefix
        for child in self.children:
            child.register()

class ApiEndpoint(EndPoint):

    def __init__(self, app, name, prefix=None):
        super(ApiEndpoint, self).__init__(app, prefix=prefix, name=name)

class ResourceEndpoint(ApiEndpoint):
    def __init__(self, app, name, prefix=None):
        super(ResourceEndpoint, self).__init__(app, prefix=prefix, name=name)

    def create_index(self, endpoint):
        @endpoint.route('/')
        def show():
            try:
                children_index = []
                for child in self.children:
                    uri = "/%s" % child.prefix
                    children_index.append(uri)
                return jsonify(attributes=children_index)
            except:
                abort(500)

class VersionEndpoint(EndPoint):

    def __init__(self, app, prefix, name):
        super(VersionEndpoint, self).__init__(app, prefix=prefix, name=name)

    def add_child(self, child_endpoint):
        super(VersionEndpoint, self).add_child(child_endpoint)
        child_endpoint.append_prefix("%s" % self.prefix)

    def create_index(self, endpoint):
        @endpoint.route('/')
        def show():
            try:
                children_index = []
                for child in self.children:
                    uri = "/%s" % child.prefix
                    children_index.append(uri)
                return jsonify(resources=children_index)
            except:
                abort(500)
