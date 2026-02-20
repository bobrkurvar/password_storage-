import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.crud import Crud, get_db_manager
from app.domain.exceptions import NotFoundError, UnauthorizedError
from app.endpoints.schemas.user import UserForToken, UserForRegistration
from app.services.tokens import get_access_token_from_refresh, get_access_token_with_password_verify
from app.services.users import user_registration
from shared.adapters.redis import RedisService, get_redis_service

router = APIRouter(prefix="/auth", tags=["own"])
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
redisServiceDep = Annotated[RedisService, Depends(get_redis_service)]


@router.post("")
async def registration(manager: dbManagerDep, user: UserForRegistration):
    return await user_registration(manager, user.user_id, user.password, user.username)


@router.post("/")
async def authorization(
    manager: dbManagerDep, redis_service: redisServiceDep, user: UserForToken
):
    try:
        log.debug("USER_ID: %s", user.user_id)
        if user.password is None:
            return await get_access_token_from_refresh(manager, redis_service, user.user_id)
        else:
            return await get_access_token_with_password_verify(manager, redis_service, user.password, user.user_id)
    except NotFoundError:
        log.debug("Token not exists")
        raise HTTPException(status_code=409)
    except UnauthorizedError as err:
        raise HTTPException(status_code=401, detail=err.detail)
