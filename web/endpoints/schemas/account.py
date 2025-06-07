from pydantic import BaseModel

class AccInput(BaseModel):
    name: str
    password: str
    user_id: int = 0