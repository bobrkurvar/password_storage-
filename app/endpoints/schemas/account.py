from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AccInput(BaseModel):
    user_id: int


class AccOutput(BaseModel):
    id: int
    user_id: int


class AccUpdate(BaseModel):
    resource: str | None = None
    password: str | None = None


class ParamItem(BaseModel):
    acc_id: int
    name: str
    content: int | str
    secret: bool



# class ParamsInput(BaseModel):
#     acc_id: int
#     items: List[ParamItem]
#     model_config = {
#         "json_schema_extra": {
#             "example": {
#                 "acc_id": 123,
#                 "items": [
#                     {"id": 1, "name": "item1", "content": 10},
#                     {"id": 2, "name": "item2", "content": 20},
#                 ],
#             }
#         }
#     }
