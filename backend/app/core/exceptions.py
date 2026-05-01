class APIException(Exception):
    def __init__(self, code: int = 400, msg: str = "业务异常"):
        self.code = code
        self.msg = msg