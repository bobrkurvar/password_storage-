import logging
from app.domain import CredentialsValidateError, NotFoundError, RefreshTokenExpireError, User, Role, InvalidAccessTokenError, AccessError
from app.infra.security import verify

log = logging.getLogger(__name__)


async def create_tokens_and_save_refresh(user_id, redis_service, manager, tokens_manager):
    refresh_time = 86400 * 7
    try:
        user_roles = (
            await manager.read(
                User,
                id=user_id,
                to_join=[
                    "roles",
                ],
            )
        )[0]
        roles = user_roles["roles_names"]
    except IndexError:
        roles = []
    refresh_token = tokens_manager.create_refresh_token(
        {"sub": str(user_id), "roles": roles, "type": "refresh"}
    )
    refresh_key = f"{user_id}:refresh_token"
    await redis_service.set(
        refresh_key,
        value=refresh_token,
        ttl=refresh_time,
    )
    return tokens_manager.create_access_token({"sub": str(user_id), "roles": roles, "type": "access"})


async def get_user(manager, user_id: int = None, username: str | None = None):
    if user_id is None:
        ident, ident_val = "username", username
        cur = await manager.read(User, username=username)
    else:
        ident, ident_val = "id", user_id
        cur = await manager.read(User, id=int(user_id))
    try:
        return cur[0]
    except IndexError:
        log.debug("USER NOT FOUND")
        raise NotFoundError(User, ident, ident_val)


async def get_access_token_from_login(
    redis_service, manager, tokens_manager, password: str, user_id: int
):
    user = await get_user(manager, user_id)
    if verify(password, user.get("password")):
        log.debug("password verify")
        return await create_tokens_and_save_refresh(user_id, redis_service, manager, tokens_manager)
    else:
        raise CredentialsValidateError


async def get_access_token_from_refresh(manager, redis_service, tokens_manager, user_id: int):
    log.debug("get from refresh token")
    await get_user(manager, user_id)
    refresh_key = f"{user_id}:refresh_key"
    refresh_token = await redis_service.get(refresh_key)
    if refresh_token:
        tokens_manager.check_refresh_token(refresh_token, user_id)
        return await create_tokens_and_save_refresh(user_id, redis_service, manager, tokens_manager)
    else:
        log.debug("refresh token not exists")
        raise RefreshTokenExpireError



def user_info_from_token(token, tokens_manager):
    data = tokens_manager.get_payload(token)
    log.debug("auth service, data: %s", data)
    user_id = data.get("sub")
    roles = data.get("roles")
    if user_id is None:
        log.debug("user_id is None")
        raise InvalidAccessTokenError
    user = {"user_id": int(user_id), "roles": roles}
    return user



async def user_roles(manager, user: dict, required_roles: list):
    roles = user.get("roles")
    if "admin" in roles or "moderator" in roles:
        log.debug("управляющая роль проверка роли за базы данных")
        roles = await manager.read(
            Role,
            ident="user_id",
            ident_val=int(user.get("user_id")),
            to_join="users_roles",
        )
        roles = [role.get("role_name") for role in roles]
    log.debug("проверка роли %s на присутствие в %s", roles, required_roles)
    log.debug("user role %s", roles)
    if all(role not in required_roles for role in roles):
        raise AccessError
    return user