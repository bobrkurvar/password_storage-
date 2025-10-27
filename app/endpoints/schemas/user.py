from typing import Optional

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    id: int | None = None
    password: str
    username: str
    salt: str


class UserOutput(BaseModel):
    username: str
    id: int
    salt: str


class OutputToken(BaseModel):
    access_token: str
    refresh_token: str


class UserRolesInput(BaseModel):
    user_id: int | None = None
    role_name: str | None = None
    role_id: int | None = None


class UserRolesOutput(BaseModel):
    role_name: str | None = None
    role_id: int
