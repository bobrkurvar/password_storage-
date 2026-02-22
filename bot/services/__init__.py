from enum import Enum


class AuthStage(Enum):
    OK = "ok"
    NEED_PASSWORD = "need_password"
    WRONG_PASSWORD = "wrong_password"
    NEED_REGISTRATION = "need_registration"
    NEED_UNLOCK = "need_unlock"
