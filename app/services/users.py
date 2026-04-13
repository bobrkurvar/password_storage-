import logging
from app.domain import CredentialsValidateError, User, UserRole, ManyAuthRequestsError
from app.services.UoW import UnitOfWork
from app.infra.security import derive_master_key, get_password_hash, get_salt, verify, encrypt_dek, generate_dek, decrypt_dek

log = logging.getLogger(__name__)



async def user_registration(
    manager, user_id: int, password: str, username: str, uow_class=UnitOfWork
):
    # регистрация пользователя
    salt = get_salt()
    kek = derive_master_key(password, salt)
    dek = generate_dek()
    encrypted_dek = encrypt_dek(dek, kek)
    async with uow_class(manager._session_factory) as uow:
        user = await manager.create(
            User,
            id=user_id,
            password=get_password_hash(password),
            username=username,
            salt=salt,
            encrypted_dek = encrypted_dek,
            session=uow.session,
        )
        is_admin = await manager.read(UserRole, user_id=user_id, role_name="admin", session=uow.session)
        role_name = "admin" if is_admin else "user"
        await manager.create(
            UserRole, role_name=role_name, user_id=user["id"], session=uow.session
        )
        return user


async def get_dek_from_redis_or_password(redis_service, manager, user_id: int, password: str | None = None):
    redis_dek_key = f"{user_id}:dek"
    dek = await redis_service.get(redis_dek_key)
    if dek is None and password:
        user = (await manager.read(User, id=user_id))[0]
        if verify(password, user.get("password")):
            kek = derive_master_key(password, user.get("salt"))
            dek = decrypt_dek(encrypted_dek=user["encrypted_dek"], kek=kek)
            encoded_dek= dek.decode("utf-8") # bytes → str
            await redis_service.set(redis_dek_key, encoded_dek, ttl=900)
        else:
            raise CredentialsValidateError
    if isinstance(dek, str):
        dek = dek.encode("utf-8")
    return dek


async def login_attempts(redis_service, user_id: int):
    attempts = await redis_service.incr(f"{user_id}:login_attempts")
    delay = 2 ** attempts
    blocked = await redis_service.get(f"{user_id}:blocked")
    if blocked:
        raise ManyAuthRequestsError(attempts, delay)
    await redis_service.set(f"{user_id}:blocked", 1, ttl=delay)


