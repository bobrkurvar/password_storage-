from fastapi import HTTPException


class CustomDbException(HTTPException):
    def __init__(self, message: str, detail: str, status_code: int = 400):
        HTTPException.__init__(self, status_code, detail)
        self.message = message

