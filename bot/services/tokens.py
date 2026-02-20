import base64
import logging
from enum import Enum
from bot.texts import phrases
from bot.services.users import derive_master_key


log = logging.getLogger(__name__)




class AuthStage(Enum):
    OK = "ok"
    NEED_PASSWORD = "need_password"
    WRONG_PASSWORD = "wrong_password"
    NEED_UNLOCK = "need_unlock"
    NEED_REGISTRATION = "need_registration"


async def ensure_auth(
    ext_api_manager,
    redis_service,
    user_id: int,
    password: str | None = None,
    need_crypto: bool = False,
):
    try:
        access_key = f"{user_id}:access_token"
        token = await redis_service.get(access_key)
        if token is None:
            access_token_ttl = 900
            token = await ext_api_manager.auth(user_id, password, ttl=access_token_ttl)
            await redis_service.set(access_key, token, )
        log.debug("token: %s", token)

        if token is None:
            return None, None, AuthStage.NEED_PASSWORD if password is None else None, None, AuthStage.WRONG_PASSWORD
        if not need_crypto:
            return token, None, AuthStage.OK
    except:
        return None, None, AuthStage.NEED_REGISTRATION

    redis_key = f"{user_id}:derive_key"
    derive_key_str = await redis_service.get(redis_key)

    if derive_key_str:
        derive_key = base64.b64decode(derive_key_str.encode("utf-8"))
        return token, derive_key, AuthStage.OK

    if password is None:
        return token, None, AuthStage.NEED_UNLOCK

    user = await ext_api_manager.read_user(access_token=token)
    salt = user["salt"]
    derive_key = derive_master_key(password, salt)
    derive_key_str = base64.b64encode(derive_key).decode("utf-8")
    await redis_service.set(redis_key, derive_key_str, ttl=900)

    return token, derive_key, AuthStage.OK



def match_status_and_interface(
    status: AuthStage,
    ok_text: str | None = None,
    ok_buttons: tuple | None = ("MENU",),
):
    text, buttons, state = None, ("MENU",), None
    match status:
        case AuthStage.OK:
            return ok_text, ok_buttons
        case AuthStage.NEED_UNLOCK:
            return (
                "Введите master password для разблокировки хранилища",
                ("MENU",),
            )
        case AuthStage.NEED_REGISTRATION:
            return phrases.need_register, ("MENU",)
        case AuthStage.NEED_PASSWORD:
            return phrases.login, ("MENU",)
        case AuthStage.WRONG_PASSWORD:
            return (
                "Неверный пароль, введите заново",
                ("MENU",),
            )

    return text, buttons

