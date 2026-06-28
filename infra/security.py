import base64
import logging
import os

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from core import conf

log = logging.getLogger(__name__)


def encrypt_account_content(plain_text: str, dek: bytes) -> str:
    f = Fernet(dek)
    return f.encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_account_content(content: str, dek: bytes) -> str:
    f = Fernet(dek)
    return f.decrypt(content.encode("utf-8")).decode("utf-8")


def derive_master_key(user_password: str, salt: str) -> bytes:
    """
    Из пользовательского пароля создаётся KEK
    (Key Encryption Key), которым шифруется DEK.
    """
    salt_bytes = base64.b64decode(salt.encode("utf-8"))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(user_password.encode("utf-8")))


def get_password_hash(password: str) -> str:
    combined = (password + conf.pepper).encode("utf-8")
    hashed = bcrypt.hashpw(combined, bcrypt.gensalt())
    return hashed.decode("utf-8")


def get_salt() -> str:
    return base64.b64encode(os.urandom(16)).decode("utf-8")


def verify(password: str, hashed: str) -> bool:
    combined = (password + conf.pepper).encode("utf-8")
    return bcrypt.checkpw(combined, hashed.encode("utf-8"))


def generate_dek() -> bytes:
    """
    Генерирует случайный DEK (Data Encryption Key).
    Fernet.generate_key() возвращает готовый ключ Fernet в bytes.
    """
    return Fernet.generate_key()


def encrypt_dek(dek: bytes, kek: bytes) -> str:
    """
    Шифрует DEK с помощью KEK.
    В базе лучше хранить строку.
    """
    f = Fernet(kek)
    return f.encrypt(dek).decode("utf-8")


def decrypt_dek(encrypted_dek: str, kek: bytes) -> bytes:
    """
    Расшифровывает DEK с помощью KEK.
    """
    f = Fernet(kek)
    return f.decrypt(encrypted_dek.encode("utf-8"))