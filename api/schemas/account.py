from pydantic import BaseModel
from typing import Any


class AccountInput(BaseModel):
    name: str
    public_data: dict[str, Any]
    secret_data: dict[str, Any]
    master_password: str | None = None


class AccountOutput(BaseModel):
    id: int
    user_id: int
    name: str
    password: str


class AccountSearch(BaseModel):
    user_id: int
    name: str