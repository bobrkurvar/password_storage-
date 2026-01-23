import logging
from bot.lexicon import phrases
from services.shared import MyExternalApiForBot
from services.shared.redis import RedisService
from enum import Enum
from core.security import derive_master_key

# class TokenStatus(Enum):
#     SUCCESS = "success"
#     NEED_PASSWORD = "need_password"
#     NEED_REGISTRATION = "need_registration"

log = logging.getLogger(__name__)

# async def token_get_flow(ext_api_manager: MyExternalApiForBot, user_id: int, password: str | None = None):
#     text = phrases.start
#     buttons = ("MENU",)
#     status = TokenStatus.SUCCESS
#     token, derive_key = None, None
#     log.debug("PASSWORD IN BOT: %s", password)
#     try:
#         token, derive_key = await ext_api_manager.token(user_id, password)
#         if not token or not derive_key:
#             if password is not None:
#                 text = "Неправильный пароль"
#                 buttons = ("MENU", "SIGN IN")
#             else:
#                 text = phrases.login
#                 status = TokenStatus.NEED_PASSWORD
#     except:
#         log.debug("USER NOT REGISTER")
#         text = phrases.register
#         status = TokenStatus.NEED_REGISTRATION
#
#     return token, derive_key, text, buttons, status


class AuthStage(Enum):
    OK = "ok"
    NEED_PASSWORD = "need_password"
    WRONG_PASSWORD = "wrong_password"
    NEED_UNLOCK = "need_unlock"
    NEED_REGISTRATION = "need_registration"



async def ensure_auth(
    ext_api_manager: MyExternalApiForBot,
    redis_service: RedisService,
    user_id: int,
    password: str | None = None,
    need_crypto: bool = False,
):
    try:
        token = await ext_api_manager.token(user_id, password)

        if token is None:
            if password is None:
                return None, None, AuthStage.NEED_PASSWORD
            else:
                return None, None, AuthStage.WRONG_PASSWORD
        if not need_crypto:
            return token, None, AuthStage.OK
    except:
        return None, None, AuthStage.NEED_REGISTRATION

    redis_key = f"{user_id}:derive_key"
    derive_key = await redis_service.get(redis_key)

    if derive_key:
        return token, derive_key, AuthStage.OK

    if password is None:
        return token, None, AuthStage.NEED_UNLOCK

    user = await ext_api_manager.read_user(access_token=token)
    salt = user["salt"]
    derive_key = derive_master_key(password, salt)
    await redis_service.set(redis_key, derive_key)

    return token, derive_key, AuthStage.OK


async def match_status_and_interface(
    ext_api_manager: MyExternalApiForBot,
    redis_service: RedisService,
    user_id: int,
    ok_text: str | None = None,
    ok_buttons: tuple | None = ("MENU", ),
    password: str | None = None,
    need_crypto: bool = False
):
    token, derive_key, status = await ensure_auth(ext_api_manager, redis_service, user_id, password, need_crypto)
    text, buttons, state = None, ("MENU",), None
    match status:
        case AuthStage.OK:
            return AuthStage.OK, token, derive_key, ok_text, ok_buttons
        case AuthStage.NEED_UNLOCK:
            return AuthStage.NEED_UNLOCK, token, None, "Введите master password для разблокировки хранилища", ("MENU", )
        case AuthStage.NEED_REGISTRATION:
            return AuthStage.NEED_REGISTRATION, None, None, phrases.register, ("MENU",)
        case AuthStage.NEED_PASSWORD:
            return AuthStage.NEED_PASSWORD, None, None, phrases.login, ("MENU",)
        case AuthStage.WRONG_PASSWORD:
            return AuthStage.WRONG_PASSWORD, None, None, "Неверный пароль, введите заново", ("MENU", )

    return status, token, derive_key, text, buttons
