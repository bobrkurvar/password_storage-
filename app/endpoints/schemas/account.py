from pydantic import BaseModel

class AccInput(BaseModel):
    resource: str
    password: str
    user_id: int = 0

class AccUpdate(BaseModel):
    resource: str | None = None
    password: str | None = None