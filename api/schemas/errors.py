from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    code: int


class CustomExceptionModel(BaseModel):
    status_code: int
    er_message: str
    er_details: str
