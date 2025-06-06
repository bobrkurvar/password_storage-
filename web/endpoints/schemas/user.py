from pydantic import BaseModel

class UserInput(BaseModel):
    id: int
    username: str
    password: str

class OutputUser(BaseModel):
    id: int | str