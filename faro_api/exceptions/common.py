from werkzeug.exceptions import HTTPException


class FaroException(HTTPException):
    code = 500


class UnknownError(FaroException):
    code = 500
    information = "Unknown error has occured"


class NotFound(FaroException):
    code = 404
    information = "Check your link for correctness"
