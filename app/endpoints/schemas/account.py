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


class AccUpdate(BaseModel):
    resource: str | None = None
    password: str | None = None


class ParamOutput(BaseModel):
    acc_id: int
    name: str
    content: int | str
    secret: bool


class ParamItem(BaseModel):
    name: str
    content: int | str
    secret: bool = False


class ParamInput(BaseModel):
    acc_id: int
    items: list[ParamItem]
