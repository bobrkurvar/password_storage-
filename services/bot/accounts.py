import base64
from core.security import encrypt_account_content

def make_secret(content: str, master_password: str, salt: str):
    salt = base64.b64decode(salt.encode("utf-8"))
    content = encrypt_account_content(content, master_password, salt)
    content = base64.b64encode(content).decode("utf-8")
    return content