from enum import StrEnum
from dataclasses import dataclass
from typing import Any

class Operations(StrEnum):
    exact = "exact"
    gte = "gte"
    lte = "lte"
    gt = "gt"
    lt = "lt"
    ilike = "ilike"
    in_ = "in"
    ne = "ne"
    is_ = "is"
    is_not = "is_not"



@dataclass
class Operation:
    value: Any
    op: Operations