import base64
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from passlib.hash import bcrypt

from app.exceptions.custom_errors import UnauthorizedError
from core import conf
from db import Crud, get_db_manager
from db.models import Roles

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)
secret_key = conf.secret_key
algorithm = conf.algorithm
log = logging.getLogger(__name__)


def get_password_hash(password: str) -> str:
    hash_password = bcrypt.hash(password)
    return hash_password


def verify(plain_password: str, password_hash: str) -> bool:
    return bcrypt.verify(plain_password, password_hash)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(days=7)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)


def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
    log.debug("Starting get_user_from_token")
    try:
        log.debug("token %s", token)
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        log.debug("Decoded payload: %s", payload)
        user_id = payload.get("sub")
        roles = payload.get("roles")
        if user_id is None:
            log.debug("user_id is None")
            raise UnauthorizedError(validate=True)
        user = {"user_id": user_id, "roles": roles}
        #user = {"user_id": user_id}
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(refresh_token=True)
    except jwt.InvalidTokenError:
        raise UnauthorizedError(access_token=True)
    return user


getUserFromTokenDep = Annotated[dict, Depends(get_user_from_token)]
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


def make_role_checker(required_role: list):
    async def check_user_roles(manager: dbManagerDep, user: getUserFromTokenDep):
        roles = user.get("roles")
        if "admin" in roles or "moderator" in roles:
            log.debug('управляющая роль проверка роли за базы данных')
            roles = (
                await manager.read(
                    model=Roles,
                    ident="user_id",
                    ident_val=int(user.get("user_id")),
                    to_join="users_roles",
                )
            )
            roles = [role.get("role_name") for role in roles]
        log.debug("проверка роли %s на присутствие в %s", roles, required_role)
        log.debug("user role %s", roles)
        if all(role not in required_role for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="не доступно"
            )
        return user

    return check_user_roles


# --- 1. Генерация ключа из мастер-пароля пользователя ---
def derive_master_key(user_password: str, salt: bytes) -> bytes:
    """
    Из пользовательского пароля (введённого при логине)
    создаётся мастер-ключ, используемый для шифрования данных.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(user_password.encode()))


# --- 2. Шифрование паролей аккаунтов с помощью мастер-ключа ---
def encrypt_account_content(
    account_password: str, master_password: str, salt: bytes | None = None
) -> bytes:
    """
    Шифрует пароль аккаунта, используя мастер-пароль пользователя.
    Возвращает salt + зашифрованные данные.
    """
    salt = os.urandom(16) if salt is None else salt
    master_key = derive_master_key(master_password, salt)
    f = Fernet(master_key)
    encrypted = f.encrypt(account_password.encode())
    return salt + encrypted


# --- 3. Расшифровка ---
def decrypt_account_content(token: bytes, master_password: str) -> str:
    """
    Расшифровывает пароль аккаунта с помощью введённого мастер-пароля.
    """
    salt, encrypted = token[:16], token[16:]
    master_key = derive_master_key(master_password, salt)
    f = Fernet(master_key)
    return f.decrypt(encrypted).decode()
