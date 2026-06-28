import logging
from typing import Annotated

from fastapi import Depends, Header
from starlette.requests import HTTPConnection
from shared.adapters.redis import RedisService
from db.mapper import registry
from infra.auth import get_user_id_with_compare_key
from services.users import get_dek_from_redis
from dto import UserForStorage

from .uow import UnitOfWork

log = logging.getLogger(__name__)


def get_uow(request: HTTPConnection):
    db_provider = request.app.state.db_provider
    if db_provider is None:
        raise RuntimeError("db connection is not initialized")
    return UnitOfWork(provider=db_provider, registry=registry)


def get_redis(request: HTTPConnection) -> RedisService:
    provider = request.app.state.redis
    if provider is None:
        raise RuntimeError("Redis connection is not initialized")
    return RedisService(redis=provider.client)


def get_user_id_from_header(
    x_telegram_user_id: Annotated[int, Header()],
    x_internal_api_key: Annotated[str, Header()],
) -> int:
    return get_user_id_with_compare_key(api_key=x_internal_api_key, user_id=x_telegram_user_id)


async def get_unlocked_dek(
    user_id: "UserIdDep",
    redis: "RedisDep",
) -> UserForStorage:
    dek =  await get_dek_from_redis(user_id=user_id, redis_service=redis)
    return UserForStorage(dek=dek, id=user_id)


UowDep = Annotated[UnitOfWork, Depends(get_uow)]
RedisDep = Annotated[RedisService, Depends(get_redis)]
UserIdDep = Annotated[int, Depends(get_user_id_from_header)]
UserForStorageDep = Annotated[UserForStorage, Depends(get_unlocked_dek)]

