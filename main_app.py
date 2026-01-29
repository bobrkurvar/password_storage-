from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from app.endpoints import main_router
#from app.exceptions.handlers import *
from shared.adapters.redis import get_redis_client, init_redis_service
from app.adapters.crud import get_db_manager
import logging

dep = []

log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = get_redis_client()
    redis_conn = await redis_client.init_redis()
    redis_service = init_redis_service(prefix="api", redis_conn=redis_conn)
    if redis_conn:
        await FastAPILimiter.init(redis_conn)
        dep.append(Depends(RateLimiter(times=5, seconds=10)))
    else:
        log.debug("don't init ratelimiter")

    yield

    manager = get_db_manager()
    await redis_client.close_redis()
    await manager.close_and_dispose()
    await redis_service.redis.close()



app = FastAPI(lifespan=lifespan, dependencies=dep)

app.include_router(main_router)
# app.add_exception_handler(NotFoundError, not_found_in_db_exceptions_handler)
# app.add_exception_handler(
#     AlreadyExistsError, entity_already_exists_in_db_exceptions_handler
# )
# app.add_exception_handler(
#     CustomForeignKeyViolationError, foreign_key_violation_exceptions_handler
# )
# app.add_exception_handler(DatabaseError, data_base_exception_handler)
# app.add_exception_handler(UnauthorizedError, no_auth_exception_handler)
#
# app.add_exception_handler(Exception, global_exception_handler)
