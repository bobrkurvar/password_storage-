import logging
from services import CredentialsValidateError, ManyAuthRequestsError
from dto import CreateUserDto, ReadUserDto
from infra.security import derive_master_key, get_salt, verify, encrypt_dek, generate_dek, decrypt_dek

log = logging.getLogger(__name__)



async def user_registration(uow, password: str, username: str):
    salt = get_salt()
    kek = derive_master_key(password, salt)
    dek = generate_dek()
    encrypted_dek = encrypt_dek(dek, kek)
    user_dto = CreateUserDto(password=password, username=username, salt=salt, encrypted_dek=encrypted_dek)
    async with uow:
        return await uow.db.create(user_dto)


async def get_dek_from_redis(redis_service, user_id: int):
    redis_dek_key = f"{user_id}:dek"
    dek = await redis_service.get(redis_dek_key)
    return dek.encode("utf-8") if isinstance(dek, str) else dek


async def get_dek_from_password(uow, redis_service, user_id: int, password: str):
    user = await uow.db.read_one(ReadUserDto, id=user_id, with_raise=True)
    if verify(password, user.get("password")):
        redis_dek_key = f"{user_id}:dek"
        kek = derive_master_key(password, user.get("salt"))
        dek = decrypt_dek(encrypted_dek=user["encrypted_dek"], kek=kek)
        encoded_dek= dek.decode("utf-8") # bytes → str
        await redis_service.set(redis_dek_key, encoded_dek, ttl=900)
    else:
        raise CredentialsValidateError
    return dek.encode("utf-8") if isinstance(dek, str) else dek

# async def get_dek_from_redis_or_password(uow, redis_service, user_id: int, password: str | None = None):
#     redis_dek_key = f"{user_id}:dek"
#     dek = await redis_service.get(redis_dek_key)
#     if dek is None and password:
#         user = await uow.db.read_one(ReadUserDto, id=user_id)
#         if verify(password, user.get("password")):
#             kek = derive_master_key(password, user.get("salt"))
#             dek = decrypt_dek(encrypted_dek=user["encrypted_dek"], kek=kek)
#             encoded_dek= dek.decode("utf-8") # bytes → str
#             await redis_service.set(redis_dek_key, encoded_dek, ttl=900)
#         else:
#             raise CredentialsValidateError
#     if isinstance(dek, str):
#         dek = dek.encode("utf-8")
#     return dek


async def login_attempts(redis_service, user_id: int):
    attempts = await redis_service.incr(f"{user_id}:login_attempts")
    delay = 2 ** attempts
    blocked = await redis_service.get(f"{user_id}:blocked")
    if blocked:
        raise ManyAuthRequestsError(attempts, delay)
    await redis_service.set(f"{user_id}:blocked", 1, ttl=delay)


