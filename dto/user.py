from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, slots=True)
class UserForStorage:
    id: int
    dek: bytes


@dataclass(frozen=True, slots=True)
class CreateUserDto:
    username: str
    password: str
    salt: str
    encrypted_dek: str



@dataclass(frozen=True, slots=True)
class ReadUserDto:
    id: int
    username: str