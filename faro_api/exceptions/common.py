import werkzeug.exceptions as http


class FaroException(http.HTTPException):
    code = 500

    def __init__(self, **kwargs):
        if 'information' in kwargs:
            self.information = kwargs['information']


class UnknownError(FaroException):
    code = 500
    information = "Unknown error has occured"


class InvalidInput(FaroException):
    code = 400
    information = "Incorrect arguments or bad syntax"


class RequiresBody(InvalidInput):
    information = "Empty body"


class Forbidden(FaroException):
    code = 403
    information = "Forbidden."


class NotFound(FaroException):
    code = 404
    information = "Check your link for correctness"
