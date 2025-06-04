from pydantic import BaseModel

class CustomExceptionModel(BaseModel):
    status_code: str | int
    er_message: str
    er_details: str