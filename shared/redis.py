import logging

from redis.asyncio import ConnectionError, Redis

from core import conf

log = logging.getLogger(__name__)

host = conf.redis_host


async def init_redis() -> Redis | None:
    redis = Redis(host=host)

    try:
        await redis.ping()
        return redis
    except ConnectionError:
        log.debug("У объекта redis закрылось соединение")
        try:
            await redis.close()
            await redis.connection_pool.disconnect()
        except Exception:
            pass
        finally:
            return None


async def close_redis(redis: Redis):
    try:
        await redis.close()
        await redis.connection_pool.disconnect()
    except Exception:
        pass
