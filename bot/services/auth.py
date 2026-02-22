import logging

from bot.services import AuthStage
from bot.services.exceptions import (AuthError, UnauthorizedError,
                                     UnlockStorageError)
from bot.texts import phrases

log = logging.getLogger(__name__)


async def ensure_auth(
    ext_api_manager,
    redis_service,
    user_id: int,
    password: str | None = None,
):
    try:
        access_key = f"{user_id}:access_token"
        token = await redis_service.get(access_key)
        if token is None:
            token = await ext_api_manager.auth(user_id, password)
            await redis_service.set(
                access_key,
                token,
                ttl = 900
            )
        log.debug("token: %s", token)
        return token, AuthStage.OK
    except UnauthorizedError as exc:
        if exc.registration:
            raise AuthError(AuthStage.NEED_REGISTRATION)
        else:
            raise AuthError(
                AuthStage.NEED_PASSWORD
                if password is None
                else AuthStage.WRONG_PASSWORD
            )


async def action_with_unlock_storage(
        action,
        access_token: str | None = None,
        http_client = None,
        password: str | None = None,
):
    if password is not None and http_client is not None:
        try:
            await http_client.master_key(access_token=access_token, password=password)
            log.debug("TOKEN IN action_with_unlock_storage: %s", access_token)
            return await action()
        except UnauthorizedError:
            raise AuthError(AuthStage.WRONG_PASSWORD)
    else:
        try:
            return await action()
        except UnlockStorageError:
            raise AuthError(AuthStage.NEED_UNLOCK)


# async def action_with_unlock_storage(
#         action,
#         *args,
#         access_token: str | None = None,
#         http_client = None,
#         password: str | None = None,
#         **kwargs
# ):
#     try:
#         await action(*args, **kwargs)
#     except UnlockStorageError:
#         if password is not None and http_client is not None:
#             try:
#                 await http_client.master_key(access_token=access_token, password=password)
#                 await action(*args, **kwargs)
#             except UnauthorizedError:
#                 raise AuthError(AuthStage.WRONG_PASSWORD)
#         raise AuthError(AuthStage.NEED_UNLOCK)


def match_status_and_interface(
    status: AuthStage = AuthStage.OK,
    ok_text: str | None = None,
    ok_buttons: tuple | None = ("MENU",),
):
    match status:
        case AuthStage.OK:
            return ok_text, ok_buttons
        case AuthStage.NEED_REGISTRATION:
            return phrases.need_register, ("MENU",)
        case AuthStage.NEED_UNLOCK:
            return phrases.need_unlock, ("MENU",)
        case AuthStage.NEED_PASSWORD:
            return phrases.login, ("MENU",)
        case AuthStage.WRONG_PASSWORD:
            return phrases.wrong_password, ("MENU",)
