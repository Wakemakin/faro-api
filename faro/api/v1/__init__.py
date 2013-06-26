import api.common as api


class Version1Endpoint(api.VersionEndpoint):
    vpfx = "v1.0"

    def __init__(self, app):
        super(Version1Endpoint, self).__init__(app, self.vpfx, self.vpfx)
