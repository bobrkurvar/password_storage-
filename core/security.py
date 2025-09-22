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
from fastapi import Depends
from app.exceptions.custom_errors import UnauthorizedError
from fastapi.security.oauth2 import OAuth2PasswordBearer
from passlib.hash import bcrypt

from core import conf

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
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        user_id = payload.get("sub")
        if user_id is None:
            log.debug("user_id is None")
            raise UnauthorizedError(validate=True)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(refresh=True)
    except jwt.InvalidTokenError:
        raise UnauthorizedError(validate=True)
    return user_id


getUserFromTokenDep = Annotated[int, Depends(get_user_from_token)]


# 1. Из пароля делаем ключ
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # используем SHA-256
        length=32,  # длина ключа = 32 байта (256 бит)
        salt=salt,  # соль (16 байт случайных данных)
        iterations=100_000,  # количество итераций (чем больше, тем медленнее brute-force)
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


# 2. Шифрование
def encrypt(data: str, password: str) -> bytes:
    salt = os.urandom(16)  # соль для KDF
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return salt + encrypted  # соль приклеиваем к началу, чтобы не хранить отдельно


# 3. Расшифрование
def decrypt(token: bytes, password: str) -> str:
    salt, encrypted = token[:16], token[16:]
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(encrypted).decode()
