from fastapi import HTTPException, status

class CustomDbException(HTTPException):
    def __init__(self, message: str, detail: str, status_code: status.HTTP_404_NOT_FOUND):
        HTTPException.__init__(self, status_code, detail)
        self.message = message

