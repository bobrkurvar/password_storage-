import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.adapters.generic_repo import get_db_manager
from api.endpoints import main_router
from core.logger import setup_logging
from shared.adapters.redis import get_redis_client

dep = []

log = logging.getLogger(__name__)

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    manager = get_db_manager()
    await manager.connect()
    redis_client = get_redis_client()
    redis_conn = await redis_client.init_redis()
    if redis_conn:
        await FastAPILimiter.init(redis_conn)
        dep.append(Depends(RateLimiter(times=10, seconds=1)))
    else:
        log.debug("don't init ratelimiter")

    yield
    await redis_client.close_redis()
    await manager.close_and_dispose()


app = FastAPI(lifespan=lifespan, dependencies=dep)

app.include_router(main_router)

