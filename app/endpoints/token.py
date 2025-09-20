import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.endpoints.schemas.user import OutputToken, UserInput
from core.security import (create_access_token, create_refresh_token,
                           getUserFromTokenDep, verify)
from db import Crud, get_db_manager
from db.models import User

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
        cur = (
            await manager.read(model=User, ident="username", ident_val=user.username)
        )[0]
    else:
        cur = (
            await manager.read(model=User, ident="id", ident_val=int(user.client_id))
        )[0]
    if not cur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    log.debug(cur.get("password"))
    if verify(user.password, cur.get("password")):
        log.debug("client_id: %s", user.client_id)
        access_token = create_access_token({"sub": user.client_id})
        refresh_token = create_refresh_token({"sub": user.client_id})
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="credentials error"
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="обновление access и refresh токенов",
    response_model=OutputToken,
)
async def update_tokens(user_id: getUserFromTokenDep, manager: dbManagerDep):
    cur = (await manager.read(model=User, ident="id", ident_val=int(user_id)))[0]
    if cur:
        access_token = create_access_token({"sub": user_id, "type": "access"})
        refresh_token = create_refresh_token({"sub": user_id, "type": "refresh"})
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
