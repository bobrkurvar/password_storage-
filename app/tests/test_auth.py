import pytest
from .conftest import fake_redis, fake_db
from .helpers import get_tokens, add_to_table, decode_token
from app.services.tokens import check_refresh_token, get_access_token_from_refresh, get_access_token_with_password_verify
from app.domain import InvalidRefreshTokenError, NotFoundError, User
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
    add_to_table(fake_db.storage, User, user)
    refresh_data = {"sub": str(user_id)}
    _, refresh_token = get_tokens(refresh_data=refresh_data)
    await fake_redis.set(f"{user_id}:refresh_key", refresh_token)
    access_token = await get_access_token_from_refresh(fake_db, fake_redis, user["id"])
    log.debug(access_token)
    data = decode_token(access_token)
    assert data["sub"] == str(user_id)
    assert data["type"] == "access"
    assert data["roles"] == ["admin"]


