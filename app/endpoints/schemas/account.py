from pydantic import BaseModel


class AccountInput(BaseModel):
    password: str
    name: str
    params: list


class AccountOutput(BaseModel):
    id: int
    user_id: int
    name: str
    password: str
