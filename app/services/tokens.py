import logging
from datetime import datetime, timedelta, timezone

import jwt

# import bcrypt
from app.domain.exceptions import (CredentialsValidateError,
                                   InvalidRefreshTokenError, NotFoundError,
                                   RefreshTokenExpireError)
from app.domain.user import User
from core import conf

from .security import verify

log = logging.getLogger(__name__)
secret_key = conf.secret_key
algorithm = conf.algorithm


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    to_encode.update({"type": "access"})
    return jwt.encode(to_encode, secret_key, algorithm)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(days=7)
    )
    to_encode.update({"exp": expire})
    to_encode.update({"type": "refresh"})
    # log.debug("refresh to_encode: %s", to_encode)
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def check_refresh_token(refresh_token: str, my_id: int):
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise RefreshTokenExpireError
    except jwt.InvalidTokenError as exc:
        log.exception("ошибка декодирования refresh токена")
        raise InvalidRefreshTokenError from exc

    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError

    if payload.get("sub") != str(my_id):
        raise InvalidRefreshTokenError


async def create_tokens_and_save_refresh(user_id, redis_service, manager):
    refresh_time = 86400 * 7
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
    refresh_token = create_refresh_token(
        {"sub": str(user_id), "roles": roles, "type": "refresh"}
    )
    refresh_key = f"{user_id}:refresh_token"
    await redis_service.set(
        refresh_key,
        value=refresh_token,
        ttl=refresh_time,
    )
    return create_access_token({"sub": str(user_id), "roles": roles, "type": "access"})


#
# def verify(password: str, hashed: str) -> bool:
#     return bcrypt.checkpw(password.encode(), hashed.encode())


async def get_user_for_token(manager, user_id: int = None, username: str | None = None):
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


async def get_access_token_with_password_verify(
    redis_service, manager, password: str, user_id: int
):
    user = await get_user_for_token(manager, user_id)
    if verify(password, user.get("password")):
        log.debug("password verify")
        return await create_tokens_and_save_refresh(user_id, redis_service, manager)
    else:
        raise CredentialsValidateError


async def get_access_token_from_refresh(manager, redis_service, user_id: int):
    log.debug("get from refresh token")
    await get_user_for_token(manager, user_id)
    refresh_key = f"{user_id}:refresh_key"
    refresh_token = await redis_service.get(refresh_key)
    if refresh_token:
        check_refresh_token(refresh_token, user_id)
        return await create_tokens_and_save_refresh(user_id, redis_service, manager)
