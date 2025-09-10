from typing import Optional

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage


class InputUser(StatesGroup):
    sign_in = State()
    sign_up = State()


class InputAccount(StatesGroup):
    params = State()
    input = State()


class CustomRedisStorage(RedisStorage):
    async def set_data(self, key: StorageKey, data: dict) -> None:
        await super().set_data(key, data)

        data_key = f"fsm:{key.user_id}:{key.chat_id}:data"
        if self.state_ttl:
            await self.redis.expire(data_key, self.state_ttl)

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
        self, key: StorageKey, data: dict, *, ttl: Optional[int] = None
    ):
        # забираем ttl из данных, если он там оказался
        ttl = ttl or data.pop("ttl", None)

        # сохраняем уже очищенные данные
        await super().update_data(key, data)

        # если ttl указан -> обновляем срок жизни ключа
        if ttl is not None:
            data_key = f"fsm:{key.user_id}:{key.chat_id}:data"
            await self.redis.expire(data_key, ttl)

    async def set_state(self, key: StorageKey, state: str) -> None:
        await super().set_state(key, state)
        state_key = f"fsm:{key.user_id}:{key.chat_id}:state"
        if self.state_ttl:
            await self.redis.expire(state_key, self.state_ttl)
