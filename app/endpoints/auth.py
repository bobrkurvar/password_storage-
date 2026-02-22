import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body

from app.adapters.crud import Crud, get_db_manager
from app.domain.exceptions import NotFoundError, UnauthorizedError, CredentialsValidateError
from app.endpoints.schemas.user import UserForRegistration, UserForToken
from app.services.tokens import (get_access_token_from_refresh,
                                 get_access_token_with_password_verify)
from app.services.users import user_registration
from shared.adapters.redis import RedisService, get_redis_service
from app.adapters.auth import getUserFromTokenDep
from app.services.users import get_user_derive_key

router = APIRouter(prefix="/auth", tags=["own"])
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
redisServiceDep = Annotated[RedisService, Depends(get_redis_service)]

@router.post("/register")
async def registration(manager: dbManagerDep, user: UserForRegistration):
    return await user_registration(manager, user.user_id, user.password, user.username)

@router.post("")
async def authorization(
    manager: dbManagerDep, redis_service: redisServiceDep, user: UserForToken
):
    try:
        if user.password is None:
            return await get_access_token_from_refresh(
                manager, redis_service, user.user_id
            )
        else:
            return await get_access_token_with_password_verify(
                redis_service, manager, user.password, user.user_id
            )
    except NotFoundError:
        raise HTTPException(status_code=409)
    except UnauthorizedError as err:
        raise HTTPException(status_code=401, detail=err.detail)


@router.post("/master-key")
async def get_master_key(user: getUserFromTokenDep, user_password: Annotated[str, Body()], manager: dbManagerDep, redis_service: redisServiceDep):
    try:
        return await get_user_derive_key(redis_service, manager, int(user.get("user_id")), user_password)
    except CredentialsValidateError:
        raise HTTPException(status_code=403, detail="wrong credentials")