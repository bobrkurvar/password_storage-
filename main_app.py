import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.endpoints import main_router
from app.exceptions.handlers import *
from db import get_db_manager
from db.exceptions import *
from shared.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    if redis:
        await FastAPILimiter.init(redis)
    else:
        log.debug("don't init ratelimiter")

    yield

    manager = get_db_manager()
    if redis:
        await close_redis(redis)
    await manager.close_and_dispose()


log = logging.getLogger(__name__)

app = FastAPI(
    lifespan=lifespan, dependencies=[Depends(RateLimiter(times=5, seconds=10))]
)

app.include_router(main_router)
app.add_exception_handler(NotFoundError, not_found_in_db_exceptions_handler)
app.add_exception_handler(
    AlreadyExistsError, entity_already_exists_in_db_exceptions_handler
)
app.add_exception_handler(
    CustomForeignKeyViolationError, foreign_key_violation_exceptions_handler
)
app.add_exception_handler(DatabaseError, data_base_exception_handler)
app.add_exception_handler(UnauthorizedError, no_auth_exception_handler)

app.add_exception_handler(Exception, global_exception_handler)
