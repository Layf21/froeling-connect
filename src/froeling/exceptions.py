class AuthenticationError(BaseException):
    pass


class NetworkError(BaseException):
    def __init__(self, msg, status, url, res):
        super().__init__(f"{msg}: Status: {status}, url: {url}\nResult: {res}")
        self.status = status
        self.url = url


class ParsingError(BaseException):
    def __init__(self, msg, doc, pos, url):
        lineno = doc.count("\n", 0, pos) + 1
        colno = pos - doc.rfind("\n", 0, pos)
        errmsg = (
            f"Error while parsing API response while fetching {url}. "
            f"{msg}: line {lineno} column {colno} (char {pos})\n{doc}"
        )
        super().__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.url = url
        self.lineno = lineno
        self.colno = colno
