import logging
import os
import base64
from domain.user import User, UserRole
from core.security import get_password_hash, derive_master_key
from services.shared.redis import RedisService
from repo.UoW import UnitOfWork

log = logging.getLogger(__name__)

async def user_sign_up(manager, user_id: int, password: str, username: str):
    # регистрация пользователя
    salt = base64.b64encode(os.urandom(16)).decode("utf-8")
    async with UnitOfWork(manager._session_factory) as uow:
        user = await manager.create(
            User,
            id=user_id,
            password=get_password_hash(password),
            username=username,
            salt=salt,
            session = uow.session
        )
        is_admin = await manager.read(UserRole, user_id=user_id, role_name="admin")
        role_name = "admin" if is_admin else "user"
        await manager.create(UserRole, role_name=role_name, user_id=user["id"], session=uow.session)


async def get_derive_key(redis_service: RedisService, user_id: int, password: str | None = None, salt: bytes | None = None):
    redis_key = f"back:{user_id}_derive_key"
    if password and salt:
        derive_key = derive_master_key(password, salt)
        await redis_service.set(redis_key, derive_key)
    else:
        derive_key = await redis_service.get(redis_key)
    return derive_key