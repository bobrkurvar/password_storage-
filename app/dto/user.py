from dataclasses import dataclass
from typing import Any

# Для передачи данных в сервис
@dataclass(frozen=True, slots=True)
class CreateUserInput:
    username: str
    password: str


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