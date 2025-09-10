"""Exceptions mostly relating to web requests."""

from aiohttp.typedefs import StrOrURL


class AuthenticationError(BaseException):
    """Raised for unauthorized requests, failed reauths, or bad credentials."""

    pass


class NetworkError(BaseException):
    """Raised on unsuccessful HTTP status codes."""

    def __init__(self, msg: str, status: int, url: StrOrURL, res: str) -> None:
        """Initialize a NetworkError.

        Args:
            msg (str): Short description of the error.
            status (int): HTTP status code returned by the request.
            url (StrOrURL): The requested URL.
            res (str): Raw response body returned by the server.

        """
        super().__init__(f'{msg}: Status: {status}, url: {url}\nResult: {res}')
        self.status = status
        self.url = url


class ParsingError(BaseException):
    """Raised when parsing an API response fails.

    Attributes:
        msg (str): Short description of the parsing error.
        doc (str): The raw response text that failed to parse.
        pos (int): The character position in `doc` where the error occurred.
        url (StrOrURL): The URL that was requested.
        lineno (int): Line number of the error position.
        colno (int): Column number of the error position.

    """

    def __init__(self, msg: str, doc: str, pos: int, url: StrOrURL) -> None:
        """Initialize a ParsingError.

        Args:
            msg (str): Description of the parsing error.
            doc (str): The raw response text.
            pos (int): Character position in `doc` where the error occurred.
            url (StrOrURL): The URL that was requested.

        """
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = (
            f'Error while parsing API response while fetching {url}. {msg}: '
            f'line {lineno} column {colno} (char {pos})\n{doc}'
        )

        super().__init__(errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.url = url
        self.lineno = lineno
        self.colno = colno
