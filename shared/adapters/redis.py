import json
import logging

from redis.asyncio import ConnectionError, Redis

from core import conf

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


class RedisService:
    def __init__(self, redis=None, prefix: str = ""):
        self.prefix = prefix
        self.redis = redis

    def init_conn(self, redis):
        self.redis = redis

    def set_prefix(self, prefix: str):
        self.prefix = prefix

    async def set(
        self,
        key: str,
        value,
        ttl: int | None = None,
    ) -> None:
        key = f"{self.prefix}:{key}"
        await self.redis.set(
            key,
            json.dumps(value),
            ex=ttl,
        )

    def close(self):
        self.redis = None

    async def get(self, key: str):
        key = f"{self.prefix}:{key}"
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def delete(self, key: str) -> None:
        key = f"{self.prefix}:{key}"
        await self.redis.delete(key)

    async def pop(self, key: str):
        value = await self.get(key)
        await self.delete(key)
        return value

    async def exists(self, key: str) -> bool:
        key = f"{self.prefix}:{key}"
        return bool(await self.redis.exists(key))


redis_service = RedisService()


def init_redis_service(redis_conn, prefix: str = ""):
    redis_service.init_conn(redis_conn)
    redis_service.set_prefix(prefix)
    return redis_service


def get_redis_service():
    return redis_service
