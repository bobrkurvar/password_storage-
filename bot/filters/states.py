from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage


class InputUser(StatesGroup):
    sign_in = State()
    sign_up = State()

class InputAccount(StatesGroup):
    name = State()
    password = State()
    params = State()
    input = State()

class DeleteAccount(StatesGroup):
    choice = State()


class CustomRedisStorage(RedisStorage):
    async def set_data(self, key: StorageKey, data: dict, * , ttl: int | None = None) -> None:
        ttl = ttl or data.pop('ttl', None)
        await super().set_data(key, data)
        if ttl is not None:
            data_key = f"fsm:{key.user_id}:{key.chat_id}:data"
            await self.redis.expire(data_key, ttl)

    async def set_token(
        self, key: StorageKey, token_name: str, token_value: str, ttl: int
    ):
        data_key = f"fsm:{key.user_id}:{key.chat_id}:{token_name}"
        await self.redis.set(data_key, token_value)
        await self.redis.expire(data_key, ttl)

    async def get_token(self, key: StorageKey, token_name: str) -> str | None:
        data_key = f"fsm:{key.user_id}:{key.chat_id}:{token_name}"
        token = await self.redis.get(data_key)
        return token.decode("utf-8") if token else None

    async def update_data(
        self, key: StorageKey, data: dict, *, ttl: int | None = None
    ):
        ttl = ttl or data.pop("ttl", None)
        await super().update_data(key, data)

        if ttl is not None:
            data_key = f"fsm:{key.user_id}:{key.chat_id}:data"
            await self.redis.expire(data_key, ttl)