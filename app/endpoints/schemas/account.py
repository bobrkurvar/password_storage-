from pydantic import BaseModel


class AccountInputFromUser(BaseModel):
    user_password: str | None = None
    password: str
    name: str
    params: list


class AccountOutput(BaseModel):
    id: int
    user_id: int
    name: str
    password: str
