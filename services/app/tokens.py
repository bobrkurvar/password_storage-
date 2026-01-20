import logging
from domain.user import User, Roles
from core.security import verify, create_access_token, create_refresh_token

log = logging.getLogger(__name__)

async def get_tokens(manager, password: str, user_id: int | None = None, username: str | None = None):
    if user_id is None:
        cur = (await manager.read(model=User, ident="username", ident_val=username))[0]
    else:
        log.debug("ПОИСК ПОЛЬЗОВАТЕЛЯ В БАЗЕ ПО ID")
        cur = (
            await manager.read(model=User, ident="id", ident_val=int(user_id))
        )[0]
    if len(cur) == 0:
        return {}

    ident_val = cur.get("id")
    roles = (
        await manager.read(
            model=Roles, ident='user_id', ident_val=ident_val, to_join="users_roles"
        )
    )
    roles = [role.get("role_name") for role in roles]
    log.debug("roles: %s", roles)
    if verify(password, cur.get("password")):
        log.debug("client_id: %s", cur.get("id"))
        access_token = create_access_token({"sub": str(cur.get("id")), "roles": roles, "type": "access"})
        refresh_token = create_refresh_token({"sub": str(cur.get("id")), "roles": roles, "type": "refresh"})
        return {"access_token": access_token, "refresh_token": refresh_token}
    return {}

async def refresh_tokens(user_id: int, manager):
    cur = await manager.read(
        model=User, ident="id", ident_val=int(user_id)
    )
    roles = await manager.read(
        model=Roles,
        ident="user_id",
        ident_val=int(user_id),
        to_join=["users_roles",]
    )
    roles = [role.get("role_name") for role in roles]
    log.debug("user roles: %s", roles)
    if cur:
        access_token = create_access_token(
            {"sub": user_id, "roles": roles, "type": "access"}
        )
        refresh_token = create_refresh_token(
            {"sub": user_id, "roles": roles, "type": "refresh"}
        )
        return {"access_token": access_token, "refresh_token": refresh_token}
    return {}
