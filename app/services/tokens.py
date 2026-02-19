import logging
from app.domain.user import User
from datetime import datetime, timedelta, timezone
from core import conf
import jwt
import bcrypt
from app.domain.exceptions import NotFoundError, InvalidRefreshTokenError, RefreshTokenExpireError, CredentialsValidateError

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
    return jwt.encode(to_encode, secret_key, algorithm)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(days=7)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)


# def check_refresh_token(refresh_token: str, my_id: int):
#     try:
#         payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
#     except jwt.ExpiredSignatureError:
#         raise RefreshTokenExpireError
#     except jwt.InvalidTokenError:
#         raise InvalidRefreshTokenError
#
#     if payload.get("type") != "refresh":
#         raise InvalidRefreshTokenError
#
#     if payload.get("sub") != str(my_id):
#         raise InvalidRefreshTokenError

def check_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
    except jwt.ExpiredSignatureError:
        raise RefreshTokenExpireError
    except jwt.InvalidTokenError:
        raise InvalidRefreshTokenError

    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError

    return jwt.decode(refresh_token, secret_key, algorithms=algorithm)


async def create_dict_tokens_and_save(
    user_id, redis_client, manager
):
    access_time, refresh_time = 900, 86400 * 7
    roles = await manager.read(
        User,
        id=user_id,
        to_join=[
            "roles",
        ],
    )
    roles = [role.get("role_name") for role in roles]
    access_token = create_access_token(
        {"sub": str(user_id), "roles": roles, "type": "access"}
    )
    refresh_token = create_refresh_token(
        {"sub": str(user_id), "roles": roles, "type": "refresh"}
    )
    access_key, refresh_key = f"{user_id}:access_token", f"{user_id}:refresh_token"
    await redis_client.set(
        access_key,
        value=access_token,
        ttl=access_time,
    )
    await redis_client.set(
        refresh_key,
        value=refresh_token,
        ttl=refresh_time,
    )
    return access_token

def verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


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
        redis_client,
        manager,
        password: str,
        user_id: int | None = None,
        username: str | None = None,

):
    user = await get_user_for_token(manager, user_id, username)
    if verify(password, user.get("password")):
        log.debug("password verify")
        return await create_dict_tokens_and_save(
            user.get("id"),
            redis_client,
            manager
        )
    else:
        raise CredentialsValidateError


async def get_access_token_from_refresh(
    manager,
    redis_client,
    refresh_token: str
):
    refresh_token_payload = check_refresh_token(refresh_token)
    user_id = refresh_token_payload["sub"]
    access_token = await create_dict_tokens_and_save(
        user_id,
        redis_client,
        manager
    )
    return access_token
