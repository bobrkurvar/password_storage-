import logging
from app.domain.user import User
from datetime import datetime, timedelta, timezone
from core import conf
import jwt
import bcrypt
from app.domain.exceptions import NotFoundError, UnauthorizedError

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


def check_refresh_token(refresh_token: str, my_id: int):
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(refresh_token=True)
    except jwt.InvalidTokenError:
        raise UnauthorizedError(access_token=True)

    if payload.get("type") != "refresh":
        raise UnauthorizedError(access_token=True)

    if payload.get("sub") != str(my_id):
        raise UnauthorizedError(access_token=True)


async def create_dict_tokens_and_save(
    user_id, redis_client, roles, access_time, refresh_time, access_key, refresh_key
):
    access_token = create_access_token(
        {"sub": str(user_id), "roles": roles, "type": "access"}
    )
    refresh_token = create_refresh_token(
        {"sub": str(user_id), "roles": roles, "type": "refresh"}
    )
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

async def get_tokens(
    manager,
    redis_client,
    password: str | None = None,
    user_id: int | None = None,
    username: str | None = None,
):
    if user_id is None:
        ident, ident_val = "username", username
        cur = await manager.read(User, username=username)
    else:
        ident, ident_val = "id", user_id
        cur = await manager.read(User, id=int(user_id))
    if len(cur) == 0:
        log.debug("USER NOT FOUND")
        raise NotFoundError(User, ident, ident_val)
    cur = cur[0]
    ident_val = cur.get("id")
    access_key, refresh_key = f"{ident_val}:access_token", f"{ident_val}:refresh_token"
    access_token = await redis_client.get(access_key)
    if not access_token:
        log.info("access token не существует")
        roles = await manager.read(
            User,
            id=ident_val,
            to_join=[
                "roles",
            ],
        )
        roles = [role.get("role_name") for role in roles]
        access_time = 900
        refresh_time = 86400 * 7
        if password is not None:
            if verify(password, cur.get("password")):
                log.debug("password verify")
                access_token = await create_dict_tokens_and_save(
                    user_id,
                    redis_client,
                    roles,
                    access_time,
                    refresh_time,
                    access_key,
                    refresh_key,
                )
            else:
                raise UnauthorizedError(validate=True)
        else:
            refresh_token = await redis_client.get(refresh_key)
            if refresh_token is not None:
                log.info("refresh token существует")
                check_refresh_token(refresh_token, ident_val)
                log.info("refresh token прошёл проверку")
                access_token = await create_dict_tokens_and_save(
                    user_id,
                    redis_client,
                    roles,
                    access_time,
                    refresh_time,
                    access_key,
                    refresh_key,
                )
            else:
                raise UnauthorizedError(refresh_token=True)

    return access_token
