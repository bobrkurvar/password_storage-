from pydantic import BaseModel

class UserInput(BaseModel):
    id: int
    password: str
    username: str

class OutputUser(BaseModel):
    id: int | str