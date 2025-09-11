from typing import Optional

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    id: int | None = None
    password: str
    username: str


class UserOutput(BaseModel):
    username: str
    password: str
    id: int


class OutputToken(BaseModel):
    access_token: str
    refresh_token: str
