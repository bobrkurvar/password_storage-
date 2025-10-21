from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AccInput(BaseModel):
    id: int | None = None
    user_id: int


class AccOutput(BaseModel):
    id: int
    user_id: int


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
    items: List[ParamItem]
