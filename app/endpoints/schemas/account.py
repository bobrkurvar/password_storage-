from typing import Any, Dict, List

from pydantic import BaseModel


class AccInput(BaseModel):
    user_id: int


class AccOutput(BaseModel):
    user_id: int


class AccUpdate(BaseModel):
    resource: str | None = None
    password: str | None = None


class ParamsInput(BaseModel):
    acc_id: int
    items: List[Dict[str, Any]]


class ParamsOutput(BaseModel):
    acc_id: int
    items: List[Dict[str, Any]]
