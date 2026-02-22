import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.crud import Crud, get_db_manager
from app.endpoints.schemas.user import UserForRegistration
from app.services.users import user_registration
from shared.adapters.redis import RedisService, get_redis_service

router = APIRouter(prefix="/user", tags=["own"])
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
redisServiceDep = Annotated[RedisService, Depends(get_redis_service)]


@router.post("")
async def registration(manager: dbManagerDep, user: UserForRegistration):
    return await user_registration(manager, user.user_id, user.password, user.username)