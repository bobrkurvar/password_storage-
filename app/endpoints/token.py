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
        cur = (
            await manager.read(model=Users, ident=ident, ident_val=user.username)
        )[0]
    else:
        ident = "user_id"
        log.debug("ПОИСК ПОЛЬЗОВАТЕЛЯ В БАЗЕ ПО ID")
        cur = (
            await manager.read(model=Users, ident="id", ident_val=int(user.client_id))
        )[0]
    log.debug("ПОЛЬЗОВАТЕЛЬ ИЗ БАЗЫ: %s", cur)
    log.debug(cur.get("password"))
    ident_val = int(user.client_id) if ident == "user_id" else user.username
    roles = (await manager.read(model=Roles, ident=ident, ident_val=ident_val, to_join="users_roles"))[0]
    if verify(user.password, cur.get("password")):
        log.debug("client_id: %s", user.client_id)
        access_token = create_access_token({"sub": user.client_id, "roles": roles})
        refresh_token = create_refresh_token({"sub": user.client_id, "roles": roles})
        return {"access_token": access_token, "refresh_token": refresh_token}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="обновление access и refresh токенов",
    response_model=OutputToken,
)
async def update_tokens(user_id: getUserFromTokenDep, manager: dbManagerDep):
    cur = await manager.read(model=Users, ident="id", ident_val=int(user_id))
    roles = await manager.read(
        model=Roles, ident="user_id", ident_val=int(user_id), to_join="users_roles"
    )
    log.debug("user roles: %s", roles)
    if cur:
        access_token = create_access_token(
            {"sub": user_id, "roles": roles, "type": "access"}
        )
        refresh_token = create_refresh_token(
            {"sub": user_id, "roles": roles, "type": "refresh"}
        )
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
