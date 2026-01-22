import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from repo import Crud, get_db_manager
from services.app.users import user_sign_up
from services.app.tokens import get_tokens
from app.endpoints.schemas.user import UserForToken
from services.app.redis import get_redis_service

router = APIRouter(
    tags=[
        "Token",
    ]
)

log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
redisServiceDep = Annotated[Crud, Depends(get_redis_service)]

@router.post("/user/sign-up")
async def sign_up(manager: dbManagerDep, user: UserForToken):
    return await user_sign_up(manager, user.user_id, user.password, user.username)

@router.post("/user/token")
async def sign_in(manager: dbManagerDep, redis_service: redisServiceDep, user: UserForToken):
    try:
        return await get_tokens(manager, redis_service, user.password, user.user_id)
    except:
        log.debug("Token not exists")
        return Response(status_code=409)


# @router.post(
#     "/login",
#     status_code=status.HTTP_200_OK,
#     summary="аутентификация пользователя",
#     response_model=OutputToken,
# )
# async def login_user(
#     user: Annotated[OAuth2PasswordRequestForm, Depends()], manager: dbManagerDep
# ):
#     if user.client_id is None:
#         ident = "username"
#         log.debug("ПОИСК ПОЛЬЗОВАТЕЛЯ В БАЗЕ ПО USERNAME")
#         cur = (await manager.read(model=Users, ident=ident, ident_val=user.username))[0]
#     else:
#         log.debug("ПОИСК ПОЛЬЗОВАТЕЛЯ В БАЗЕ ПО ID")
#         cur = (
#             await manager.read(model=Users, ident="id", ident_val=int(user.client_id))
#         )[0]
#     if len(cur) == 0:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="incorrect password"
#         )
#     log.debug("ПОЛЬЗОВАТЕЛЬ ИЗ БАЗЫ: %s", cur)
#     log.debug(cur.get("password"))
#
#     ident_val = cur.get("id")
#     roles = (
#         await manager.read(
#             model=Roles, ident='user_id', ident_val=ident_val, to_join="users_roles"
#         )
#     )
#     roles = [role.get("role_name") for role in roles]
#     log.debug("roles: %s", roles)
#     if verify(user.password, cur.get("password")):
#         log.debug("client_id: %s", cur.get("id"))
#         access_token = create_access_token({"sub": str(cur.get("id")), "roles": roles, "type": "access"})
#         refresh_token = create_refresh_token({"sub": str(cur.get("id")), "roles": roles, "type": "refresh"})
#         return {"access_token": access_token, "refresh_token": refresh_token}
#     log.debug("НЕПРАВЛЬНЫЙ ПАРОЛЬ")
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, detail="incorrect password"
#     )


# @router.post(
#     "/refresh",
#     status_code=status.HTTP_200_OK,
#     summary="обновление access и refresh токенов",
#     response_model=OutputToken,
# )
# async def update_tokens(user: getUserFromTokenDep, manager: dbManagerDep):
#     cur = await manager.read(
#         model=Users, ident="id", ident_val=int(user.get("user_id"))
#     )
#     roles = await manager.read(
#         model=Roles,
#         ident="user_id",
#         ident_val=int(user.get("user_id")),
#         to_join="users_roles",
#     )
#     roles = [role.get("role_name") for role in roles]
#     log.debug("user roles: %s", roles)
#     if cur:
#         access_token = create_access_token(
#             {"sub": user.get("user_id"), "roles": roles, "type": "access"}
#         )
#         refresh_token = create_refresh_token(
#             {"sub": user.get("user_id"), "roles": roles, "type": "refresh"}
#         )
#         return {"access_token": access_token, "refresh_token": refresh_token}
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
