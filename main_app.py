import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis import Redis as Sync_redis
from redis.asyncio import ConnectionError, Redis

from app.endpoints import main_router
from app.exceptions.handlers import (exception_handler_to_error_response,
                                     global_exception_handler)
from db import get_db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(host="localhost")
    try:
        await FastAPILimiter.init(redis)
    except ConnectionError:
        log.debug("don't init ratelimiter")
    yield
    manager = get_db_manager()
    await redis.close()
    await manager.close_and_dispose()
    await redis.connection_pool.disconnect()


log = logging.getLogger(__name__)
sync_redis = Sync_redis(host="localhost")
try:
    log.debug("ping to redis")
    sync_redis.ping()
    app = FastAPI(
        lifespan=lifespan, dependencies=[Depends(RateLimiter(times=5, seconds=10))]
    )
except ConnectionError:
    log.debug("ping failed")
    app = FastAPI(lifespan=lifespan)
finally:
    sync_redis.close()
    sync_redis.connection_pool.disconnect()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    log.debug("REQUEST BODY: %s", body.decode())
    response = await call_next(request)
    return response


app.include_router(main_router)
app.add_exception_handler(HTTPException, exception_handler_to_error_response)
app.add_exception_handler(Exception, global_exception_handler)
