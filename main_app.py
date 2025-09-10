import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis

from app.endpoints import main_router
from app.exceptions.custom_errors import CustomDbException
from app.exceptions.handlers import (custom_exception_handler,
                                     global_exception_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(host="localhost")
    await FastAPILimiter.init(redis)
    yield
    await redis.close()
    await redis.connection_pool.disconnect()


app = FastAPI(
    lifespan=lifespan, dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)
log = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    log.debug("REQUEST BODY: %s", body.decode())
    response = await call_next(request)
    return response


app.include_router(main_router)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(CustomDbException, custom_exception_handler)
