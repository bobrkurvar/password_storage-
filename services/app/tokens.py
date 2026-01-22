import logging
from domain.user import User
from core.security import verify, create_access_token, create_refresh_token, check_refresh_token

log = logging.getLogger(__name__)


async def create_dict_tokens_and_save(user_id, redis_client, roles, access_time, refresh_time, access_key, refresh_key):
    access_token = create_access_token({"sub":str(user_id), "roles": roles, "type": "access"})
    refresh_token = create_refresh_token({"sub": str(user_id), "roles": roles, "type": "refresh"})
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

async def get_tokens(manager, redis_client, password: str | None = None, user_id: int | None = None, username: str | None = None):
    if user_id is None:
        cur = (await manager.read(User, username=username))
    else:
        cur = (
            await manager.read(User, id=int(user_id))
        )
        log.debug("CUR: %s", cur)
    if len(cur) == 0:
        log.debug("USER NOT FOUND")
        raise Exception
    cur = cur[0]
    ident_val = cur.get("id")
    access_key, refresh_key = f"{ident_val}:access_token", f"{ident_val}:refresh_token"
    access_token = await redis_client.get(access_key)
    if not access_token:
        log.info("access token не существует")
        roles = (
            await manager.read(
                User, id=ident_val, to_join=["roles", ]
            )
        )
        roles = [role.get("role_name") for role in roles]
        access_time = 900
        refresh_time = 86400 * 7
        log.debug("password: %s", password)
        if password is not None and verify(password, cur.get("password")):
            log.debug("password verify")
            access_token = await create_dict_tokens_and_save(user_id, redis_client, roles, access_time, refresh_time, access_key, refresh_key)
        else:
            refresh_token = await redis_client.get(refresh_key)
            if refresh_token:
                check_refresh_token(refresh_token, ident_val)
                log.info("refresh token существует")
                access_token = await create_dict_tokens_and_save(user_id, redis_client, roles, access_time, refresh_time, access_key, refresh_key)

    return access_token

