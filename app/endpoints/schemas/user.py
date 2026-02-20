from pydantic import BaseModel


class UserInput(BaseModel):
    id: int | None = None
    password: str
    username: str
    salt: str


class UserForToken(BaseModel):
    username: str | None = None
    user_id: int
    password: str | None = None

class UserForRegistration(BaseModel):
    user_id: int
    username: str
    password: str


