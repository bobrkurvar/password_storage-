from pydantic import BaseModel


class UserInput(BaseModel):
    id: int | None = None
    password: str
    username: str
    salt: str


class UserOutput(BaseModel):
    username: str
    id: int
    salt: str


class UserForToken(BaseModel):
    username: str | None = None
    user_id: int | None = None
    password: str | None = None


class UserRolesInput(BaseModel):
    user_id: int | None = None
    role_name: str | None = None
    role_id: int | None = None


class UserRolesOutput(BaseModel):
    role_name: str | None = None
    role_id: int
