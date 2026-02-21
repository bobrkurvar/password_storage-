import logging

from app.domain import User, UserRole, CredentialsValidateError
from app.services.UoW import UnitOfWork
# import bcrypt
# import os
# import base64
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from cryptography.fernet import Fernet
from .security import get_salt, get_password_hash, verify, derive_master_key

log = logging.getLogger(__name__)



# def encrypt_account_content(plain_text: str, derive_key: bytes) -> str:
#     f = Fernet(derive_key)
#     return f.encrypt(plain_text.encode()).decode("utf-8")
#
#
# # def decrypt_account_content(token: bytes, derive_key: bytes) -> str:
# #     f = Fernet(derive_key)
# #     return f.decrypt(token).decode()
#
# def derive_master_key(user_password: str, salt: str) -> bytes:
#     """
#     Из пользовательского пароля (введённого при логине)
#     создаётся мастер-ключ, используемый для шифрования данных.
#     """
#     salt = base64.b64decode(salt.encode("utf-8"))
#     kdf = PBKDF2HMAC(
#         algorithm=hashes.SHA256(),
#         length=32,
#         salt=salt,
#         iterations=200_000,
#     )
#     return base64.urlsafe_b64encode(kdf.derive(user_password.encode()))
#
#
#
# def get_password_hash(password: str) -> str:
#     salt = bcrypt.gensalt()
#     hashed = bcrypt.hashpw(password.encode(), salt)
#     return hashed.decode()
#
#
# def get_salt() -> str:
#     return base64.b64encode(os.urandom(16)).decode("utf-8")


async def user_registration(manager, user_id: int, password: str, username: str, uow_class=UnitOfWork):
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

async def get_user_derive_key(redis_service, manager, user_id: int, password: str | None = None):
    master_key_redis_key = f"{user_id}:master_key"
    key = await redis_service.get(master_key_redis_key)
    if key is None and password:
        user = manager.read(User, id=user_id)
        if verify(password, user.get("password")):
            key = derive_master_key(password, user.get("salt"))
            await redis_service(master_key_redis_key, key, ttl=900)
        else:
            raise CredentialsValidateError
    return key


