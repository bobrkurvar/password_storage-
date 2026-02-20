import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException

from app.adapters.auth import getUserFromTokenDep
from app.adapters.crud import Crud, get_db_manager
from app.domain.exceptions import NotFoundError, UnauthorizedError
from app.domain import User
from app.endpoints.schemas.user import UserOutput, UserForToken
from app.endpoints.schemas.errors import ErrorResponse
from app.services.tokens import get_tokens
from app.services.users import registration
from shared.adapters.redis import RedisService, get_redis_service

router = APIRouter(prefix="/user", tags=["own"])
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
redisServiceDep = Annotated[RedisService, Depends(get_redis_service)]


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получение пользователя по id из токена",
    response_model=UserOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Пользователь не найден",
            "model": ErrorResponse,
        }
    },
)
async def read_user_by_id(user: getUserFromTokenDep, manager: dbManagerDep):
    user = (await manager.read(User, id=user["user_id"]))[0]
    log.debug("Пользователь получен %s, %s", user.get("id"), user.get("username"))
    return user

@router.post("")
async def sign_up(manager: dbManagerDep, user: UserForToken):
    return await registration(manager, user.user_id, user.password, user.username)


@router.post("/token")
async def token(
    manager: dbManagerDep, redis_service: redisServiceDep, user: UserForToken
):
    try:
        return await get_tokens(manager, redis_service, user.password, user.user_id)
    except NotFoundError:
        log.debug("Token not exists")
        raise HTTPException(status_code=409)
    except UnauthorizedError as err:
        raise HTTPException(status_code=401, detail=err.detail)
