import json
from shared.redis import redis_client


class RedisService:
    def __init__(self, redis):
        self.redis = redis

    def init_conn(self, redis):
        self.redis = redis

    async def set(
        self,
        key: str,
        value,
        ttl: int | None = None,
    ) -> None:
        await self.redis.set(
            key,
            json.dumps(value),
            ex=ttl,
        )

    async def get(self, key: str):
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.redis.exists(key))


redis_service = RedisService(redis_client.redis)
def get_redis_service():
    return redis_service