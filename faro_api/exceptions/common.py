from faro_common.exceptions import common as exc


class FaroApiException(exc.FaroException):
    pass


class EventRequired(exc.FaroException):
    code = 409
    information = "Event required"


class OwnerRequired(exc.FaroException):
    code = 409
    information = "Owner required"


class AuthenticationRequired(exc.FaroException):
    code = 403
    information = "Authentication required"
