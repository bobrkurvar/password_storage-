from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64

def encrypt_account_content(plain_text: str, derive_key: bytes) -> str:
    f = Fernet(derive_key)
    return f.encrypt(plain_text.encode()).decode("utf-8")


# def decrypt_account_content(token: bytes, derive_key: bytes) -> str:
#     f = Fernet(derive_key)
#     return f.decrypt(token).decode()

def derive_master_key(user_password: str, salt: str) -> bytes:
    """
    Из пользовательского пароля (введённого при логине)
    создаётся мастер-ключ, используемый для шифрования данных.
    """
    salt = base64.b64decode(salt.encode("utf-8"))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(user_password.encode()))