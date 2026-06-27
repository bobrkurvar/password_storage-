import logging
from typing import Annotated

from fastapi import Depends
from starlette.requests import HTTPConnection
from shared.adapters.redis import RedisService
from app.db.mapper import registry

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




UowDep = Annotated[UnitOfWork, Depends(get_uow)]
RedisDep = Annotated[RedisService, Depends(get_redis)]

