from pydantic import BaseModel, Field
from typing import Optional

class UserInput(BaseModel):
    id: int | None = None
    password: str
    username: str

class OutputUser(BaseModel):
    id: int | str

class OutputToken(BaseModel):
    access_token: str
    refresh_token: str