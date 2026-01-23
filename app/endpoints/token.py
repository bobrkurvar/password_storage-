import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from repo import Crud, get_db_manager
from services.app.users import user_sign_up
from services.app.tokens import get_tokens
from app.endpoints.schemas.user import UserForToken
from services.shared.redis import get_redis_service, RedisService

router = APIRouter(
    tags=[
        "Token",
    ]
)

log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
redisServiceDep = Annotated[RedisService, Depends(get_redis_service)]

@router.post("/user/sign-up")
async def sign_up(manager: dbManagerDep, user: UserForToken):
    return await user_sign_up(manager, user.user_id, user.password, user.username)

@router.post("/user/token")
async def sign_in(manager: dbManagerDep, redis_service: redisServiceDep, user: UserForToken):
    try:
        token = await get_tokens(manager, redis_service, user.password, user.user_id)
        return token
    except:
        log.debug("Token not exists")
        return Response(status_code=409)

