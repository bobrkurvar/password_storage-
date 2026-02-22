import logging
import base64
from app.domain import CredentialsValidateError, User, UserRole
from app.services.UoW import UnitOfWork
from .security import derive_master_key, get_password_hash, get_salt, verify

log = logging.getLogger(__name__)



async def user_registration(
    manager, user_id: int, password: str, username: str, uow_class=UnitOfWork
):
    # регистрация пользователя
    salt = get_salt()
    async with uow_class(manager._session_factory) as uow:
        user = await manager.create(
            User,
            id=user_id,
            password=get_password_hash(password),
            username=username,
            salt=salt,
            session=uow.session,
        )
        is_admin = await manager.read(UserRole, user_id=user_id, role_name="admin")
        role_name = "admin" if is_admin else "user"
        await manager.create(
            UserRole, role_name=role_name, user_id=user["id"], session=uow.session
        )


async def get_user_derive_key(
    redis_service, manager, user_id: int, password: str | None = None
):
    master_key_redis_key = f"{user_id}:master_key"
    key = await redis_service.get(master_key_redis_key)
    if key is None and password:
        user = (await manager.read(User, id=user_id))[0]
        if verify(password, user.get("password")):
            key = derive_master_key(password, user.get("salt"))
            encoded_key = key.decode("utf-8") # bytes → str
            await redis_service.set(master_key_redis_key, encoded_key, ttl=900)
        else:
            raise CredentialsValidateError
    if isinstance(key, str):
        key = key.encode("utf-8")
    return key
