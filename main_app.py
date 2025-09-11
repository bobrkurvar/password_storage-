import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis

from app.endpoints import main_router
from db import get_db_manager
from app.exceptions.handlers import exception_handler_to_error_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(host="localhost")
    await FastAPILimiter.init(redis)
    yield
    manager = get_db_manager()
    await redis.close()
    await manager.close_and_dispose()
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
#app.add_exception_handler(HTTPException, exception_handler_to_error_response)
#app.add_exception_handler(Exception, global_exception_handler)
