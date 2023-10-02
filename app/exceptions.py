class MyException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


class ParsingException(MyException):
    """
    When file storage fails to parse at given URI
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = "ParsingException: " + self.message


class DownloadException(MyException):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = "DownloadException: " + self.message
