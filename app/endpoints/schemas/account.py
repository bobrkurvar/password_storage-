from pydantic import BaseModel
from typing import List, Dict, Any

class AccInput(BaseModel):
    user_id: int = 0

class AccUpdate(BaseModel):
    resource: str | None = None
    password: str | None = None

class ParamsInput(BaseModel):
    acc_id: int
    items: List[Dict[str, Any]]