import pytest
from app.infra.security import encrypt_account_content, decrypt_account_content
from app.services.users import derive_master_key, user_registration
from app.tests.fakes import FakeUoW
import logging

log = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_generate_master_key_encrypt_and_decrypt(manager):
    user_id, user_password, username = 1, "password", "username"
    user = await user_registration(manager, user_id, user_password, username, FakeUoW)
    key = derive_master_key(user_password, user["salt"])
    content = "content"
    content = encrypt_account_content(content, key)
    assert decrypt_account_content(content.encode('utf-8'), key) == "content"