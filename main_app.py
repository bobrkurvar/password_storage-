import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.adapters.crud import get_db_manager
from app.endpoints import main_router
from core.logger import setup_logging
from shared.adapters.redis import get_redis_client, get_redis_service

dep = []

log = logging.getLogger(__name__)

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    rmq_client = None
    setup_logging("app", rmq_client)
    manager = get_db_manager()
    manager.connect()
    redis_client = get_redis_client()
    redis_conn = await redis_client.init_redis()
    redis_service = get_redis_service(prefix="api", redis_conn=redis_conn)
    if redis_conn:
        await FastAPILimiter.init(redis_conn)
        redis_service.init_conn(redis_conn)
        dep.append(Depends(RateLimiter(times=10, seconds=1)))
    else:
        log.debug("don't init ratelimiter")

    yield
    await redis_service.close()
    await manager.close_and_dispose()


app = FastAPI(lifespan=lifespan, dependencies=dep)

app.include_router(main_router)

