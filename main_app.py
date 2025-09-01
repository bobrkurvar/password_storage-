from fastapi import FastAPI, Depends
from app.endpoints import main_router
from app.exceptions.handlers import global_exception_handler, custom_exception_handler
from app.exceptions.custom_errors import CustomDbException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(host='localhost')
    await FastAPILimiter.init(redis)
    yield
    await redis.close()
    await redis.connection_pool.disconnect()

app = FastAPI(lifespan=lifespan, dependencies=[Depends(RateLimiter(times=5, seconds=10))])

app.include_router(main_router)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(CustomDbException, custom_exception_handler)