import logging

from redis.asyncio import ConnectionError, Redis

from core import conf
from services.app.redis import RedisService

log = logging.getLogger(__name__)

host = conf.redis_host

class RedisClient:
    def __init__(self):
        self.redis = None

    async def init_redis(self) -> Redis | None:
        if self.redis:
            return self.redis
        redis = Redis(host=host)
        try:
            await redis.ping()
            self.redis = redis
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


    async def close_redis(self):
        try:
            await self.redis.close()
            await self.redis.connection_pool.disconnect()
        except Exception:
            pass


redis_client = RedisClient()
def get_redis_client():
    return redis_client

redis_service = RedisService(redis_client.redis)
def get_redis_service():
    return redis_service