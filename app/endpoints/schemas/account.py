from pydantic import BaseModel

class AccInput(BaseModel):
    resource: str
    password: str
    user_id: int = 0