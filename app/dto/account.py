from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CreateAccountDto:
    user_id: int
    name: str
    public_data: dict[str, Any]
    secret_data: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ReadAccountDto:
    id: int
    user_id: int
    name: str
    public_data: dict[str, Any]
    secret_data: dict[str, Any]