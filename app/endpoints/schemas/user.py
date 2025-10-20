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

class UserRolesInput(BaseModel):
    user_id: int
    role_name: str

class UserRolesOutput(BaseModel):
    role_name: str
    role_id: int

