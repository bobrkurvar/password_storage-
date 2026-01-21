import logging
import os
import base64
from domain.user import User, UserRoles
from core.security import get_password_hash
from services.app.tokens import get_tokens

log = logging.getLogger(__name__)

async def user_sign_up(manager, user_id: int, password: str, username: str):
    # регистрация пользователя
    salt = base64.b64encode(os.urandom(16)).decode("utf-8")
    await manager.create(
        User,
        id=user_id,
        password=get_password_hash(password),
        username=username,
        salt=salt
    )
    is_admin = await manager.read(UserRoles, user_id=user_id, role_name="admin")
    role_name = "admin" if is_admin else "user"
    await manager.craete(UserRoles, role_name=role_name)

# async def user_sign_up(state, message, ext_api_manager):
#     # регистрация пользователя
#     salt = base64.b64encode(os.urandom(16)).decode("utf-8")
#     await ext_api_manager.create(
#         prefix="user",
#         id=message.from_user.id,
#         password=get_password_hash(message.text),
#         username=message.from_user.username,
#         salt=salt,
#     )
#     admins = (await state.get_data()).get("admins")
#     role_name = "admin" if message.from_user.id in admins else "user"
#     role = (await ext_api_manager.read(prefix="user/roles", role_name=role_name))[0]
#     role_id = role.get("role_id")
#     log.debug("role_id: %s", role_id)
#     await ext_api_manager.create(
#         prefix=f"user/{message.from_user.id}/roles",
#         role_name="user",
#         role_id=role_id,
#     )

# async def user_sign_in(state, message, ext_api_manager):
#     # вход для пользователя
#     tokens = await ext_api_manager.login(
#         client_id=message.from_user.id,
#         password=message.text,
#         username=message.from_user.username,
#     )
#     log.debug("tokens %s", tokens)
#     if None in tokens.values():
#         log.debug("НЕПРАВЛЬНЫЙ ПАРОЛЬ")
#         return False
#     await state.update_data(master_password=message.text)
#     access_token = tokens.get("access_token")
#     access_time = 900
#     await state.storage.set_token(
#         state.key,
#         token_name="access_token",
#         token_value=access_token,
#         ttl=access_time,
#     )
#     refresh_token = tokens.get("refresh_token")
#     refresh_time = 86400 * 7
#     await state.storage.set_token(
#         state.key,
#         token_name="refresh_token",
#         token_value=refresh_token,
#         ttl=refresh_time,
#     )

async def user_sign_in(manager, user_id: int, password: str, username: str):
    # вход для пользователя
    # tokens = await ext_api_manager.login(
    #     client_id=message.from_user.id,
    #     password=message.text,
    #     username=message.from_user.username,
    # )
    tokens = await get_tokens(manager, password, user_id, username)
    log.debug("tokens %s", tokens)
    if not tokens:
        log.debug("НЕПРАВЛЬНЫЙ ПАРОЛЬ")
        return False
    #await state.update_data(master_password=message.text)
    access_token = tokens.get("access_token")
    access_time = 900
    # await state.storage.set_token(
    #     state.key,
    #     token_name="access_token",
    #     token_value=access_token,
    #     ttl=access_time,
    # )
    refresh_token = tokens.get("refresh_token")
    refresh_time = 86400 * 7
    # await state.storage.set_token(
    #     state.key,
    #     token_name="refresh_token",
    #     token_value=refresh_token,
    #     ttl=refresh_time,
    # )
    return {"access_token": access_token, "refresh_token": refresh_token}