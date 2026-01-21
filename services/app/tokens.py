import logging
from domain.user import User, Role
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
        cur = (await manager.read(model=User, ident="username", ident_val=username))
    else:
        cur = (
            await manager.read(model=User, ident="id", ident_val=int(user_id))
        )
    if len(cur) == 0:
        raise Exception
    cur = cur[0]
    ident_val = cur.get("id")
    access_key, refresh_key = f"{ident_val}:access_token", f"{ident_val}:refresh_token"
    access_token = await redis_client.get(access_key)
    if not access_token:
        roles = (
            await manager.read(
                model=Role, ident='user_id', ident_val=ident_val, to_join="users_roles"
            )
        )
        roles = [role.get("role_name") for role in roles]
        log.info("access token не существует")
        refresh_token = await redis_client.get(refresh_key)
        access_time = 900
        refresh_time = 86400 * 7
        if refresh_token:
            check_refresh_token(refresh_token, ident_val)
            log.info("refresh token существует")
            access_token = await create_dict_tokens_and_save(user_id, redis_client, roles, access_time, refresh_time, access_key, refresh_key)
        elif password is not None and verify(password, cur.get("password")):
            access_token = await create_dict_tokens_and_save(user_id, redis_client, roles, access_time, refresh_time, access_key, refresh_key)

    return access_token

# async def refresh_tokens(manager, user_id: int):
#     cur = await manager.read(
#         model=User, ident="id", ident_val=int(user_id)
#     )
#     roles = await manager.read(
#         model=Role,
#         ident="user_id",
#         ident_val=int(user_id),
#         to_join=["users_roles",]
#     )
#     roles = [role.get("role_name") for role in roles]
#     log.debug("user roles: %s", roles)
#     if cur:
#         access_token = create_access_token(
#             {"sub": user_id, "roles": roles, "type": "access"}
#         )
#         refresh_token = create_refresh_token(
#             {"sub": user_id, "roles": roles, "type": "refresh"}
#         )
#         return {"access_token": access_token, "refresh_token": refresh_token}
#     return {}

# async def check_tokens(manager, redis_client, user_id: int):
#     has_refresh_or_access = True
#     access_key, refresh_key = f"{user_id}:access_token", f"{user_id}:refresh_token"
#     access_token = await redis_client.get(access_key)
#     if not access_token:
#         log.info("access token не существует")
#         refresh_token = await redis_client.get(refresh_key)
#         access_time = 900
#         if refresh_token:
#             log.info("refresh token существует")
#             refresh_time = 86400 * 7
#             tokens = await refresh_tokens(manager, user_id)
#             await redis_client.set(
#                 access_key,
#                 value=tokens.get("access_token"),
#                 ttl=access_time,
#             )
#             await redis_client.set(
#                 refresh_key,
#                 value=tokens.get("refresh_token"),
#                 ttl=refresh_time,
#             )
#         else:
#             has_refresh_or_access = False
#     else:
#         log.info("access token существует")
#
#     return has_refresh_or_access
