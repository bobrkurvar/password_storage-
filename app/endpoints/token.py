import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.endpoints.schemas.user import OutputToken
from core.security import (create_access_token, create_refresh_token,
                           getUserFromTokenDep, verify)
from db import Crud, get_db_manager
from db.models import Roles, Users

router = APIRouter(
    tags=[
        "Token",
    ]
)
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="аутентификация пользователя",
    response_model=OutputToken,
)
async def login_user(
    user: Annotated[OAuth2PasswordRequestForm, Depends()], manager: dbManagerDep
):
    if user.client_id is None:
        ident = "username"
        log.debug("ПОИСК ПОЛЬЗОВАТЕЛЯ В БАЗЕ ПО USERNAME")
        cur = (await manager.read(model=Users, ident=ident, ident_val=user.username))[0]
    else:
        log.debug("ПОИСК ПОЛЬЗОВАТЕЛЯ В БАЗЕ ПО ID")
        cur = (
            await manager.read(model=Users, ident="id", ident_val=int(user.client_id))
        )[0]
    log.debug("ПОЛЬЗОВАТЕЛЬ ИЗ БАЗЫ: %s", cur)
    log.debug(cur.get("password"))
    # проверка на возврат не нужна так как возбудится исключение из репозитория
    ident_val = cur.get("id")
    roles = (
        await manager.read(
            model=Roles, ident='user_id', ident_val=ident_val, to_join="users_roles"
        )
    )
    roles = [role.get("role_name") for role in roles]
    log.debug("roles: %s", roles)
    if verify(user.password, cur.get("password")):
        log.debug("client_id: %s", cur.get("id"))
        access_token = create_access_token({"sub": str(cur.get("id")), "roles": roles, "type": "access"})
        refresh_token = create_refresh_token({"sub": str(cur.get("id")), "roles": roles, "type": "refresh"})
        return {"access_token": access_token, "refresh_token": refresh_token}
    log.debug("НЕПРАВЛЬНЫЙ ПАРОЛЬ")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="incorrect password"
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="обновление access и refresh токенов",
    response_model=OutputToken,
)
async def update_tokens(user: getUserFromTokenDep, manager: dbManagerDep):
    cur = await manager.read(
        model=Users, ident="id", ident_val=int(user.get("user_id"))
    )
    roles = await manager.read(
        model=Roles,
        ident="user_id",
        ident_val=int(user.get("user_id")),
        to_join="users_roles",
    )
    roles = [role.get("role_name") for role in roles]
    log.debug("user roles: %s", roles)
    if cur:
        access_token = create_access_token(
            {"sub": user.get("user_id"), "roles": roles, "type": "access"}
        )
        refresh_token = create_refresh_token(
            {"sub": user.get("user_id"), "roles": roles, "type": "refresh"}
        )
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
