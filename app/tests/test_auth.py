import pytest
from .conftest import fake_redis, fake_db
from .helpers import get_tokens, add_to_table, decode_token
from app.services.tokens import check_refresh_token, get_access_token_from_refresh, get_access_token_with_password_verify
from app.services.users import get_password_hash
from app.domain import InvalidRefreshTokenError, NotFoundError, User, CredentialsValidateError
import logging

log = logging.getLogger(__name__)

def test_check_refresh_token_success():
    user_id = 2
    refresh_data = {"sub": str(user_id)}
    _, refresh_token = get_tokens(refresh_data=refresh_data)
    check_refresh_token(refresh_token, user_id)


def test_check_refresh_token_fail_sub():
    # в token sub может быть только str
    user_id = 2
    refresh_data = {"sub": user_id}
    _, refresh_token = get_tokens(refresh_data=refresh_data)
    with pytest.raises(InvalidRefreshTokenError):
        check_refresh_token(refresh_token, user_id)


@pytest.mark.asyncio
async def test_get_access_token_from_refresh_without_register_user(fake_redis, fake_db):
    user_id = 2
    with pytest.raises(NotFoundError):
        await get_access_token_from_refresh(fake_db, fake_redis, user_id)


@pytest.mark.asyncio
async def test_get_access_token_from_password_without_register_user(fake_redis, fake_db):
    user_id = 2
    with pytest.raises(NotFoundError):
        await get_access_token_with_password_verify(fake_redis, fake_db, "",user_id)



@pytest.mark.asyncio
async def test_get_access_token_from_refresh_success(fake_redis, fake_db):
    user_id = 2
    user = {"id": user_id, "username": "user", "password": "password", "salt": "salt"}
    add_to_table(fake_db, User, user)
    refresh_data = {"sub": str(user_id)}
    _, refresh_token = get_tokens(refresh_data=refresh_data)
    await fake_redis.set(f"{user_id}:refresh_key", refresh_token)
    access_token = await get_access_token_from_refresh(fake_db, fake_redis, user_id)
    data = decode_token(access_token)
    assert data["sub"] == str(user_id)
    assert data["type"] == "access"
    assert data["roles"] == ["admin"]


@pytest.mark.asyncio
async def test_get_access_token_from_refresh_fail(fake_redis, fake_db):
    user_id = 2
    user = {"id": user_id, "username": "user", "password": "password", "salt": "salt"}
    add_to_table(fake_db, User, user)
    access_token = await get_access_token_from_refresh(fake_db, fake_redis, user_id)
    assert access_token is None


@pytest.mark.asyncio
async def test_get_access_token_from_password_success(fake_redis, fake_db):
    user_id = 2
    password = "password"
    hash_password = get_password_hash(password)
    user = {"id": user_id, "username": "user", "password": hash_password, "salt": "salt"}
    add_to_table(fake_db, User, user)
    access_token = await get_access_token_with_password_verify(fake_redis, fake_db, password, user_id)
    data = decode_token(access_token)
    assert data["sub"] == str(user_id)
    assert data["type"] == "access"
    assert data["roles"] == ["admin"]


@pytest.mark.asyncio
async def test_get_access_token_from_password_with_wrong_password(fake_redis, fake_db):
    user_id = 2
    password = "password"
    hash_password = get_password_hash(password)
    user = {"id": user_id, "username": "user", "password": hash_password, "salt": "salt"}
    add_to_table(fake_db, User, user)
    wrong_password = "wrong_password"
    with pytest.raises(CredentialsValidateError):
        await get_access_token_with_password_verify(fake_redis, fake_db, wrong_password, user_id)




