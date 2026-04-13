import logging

import pytest

from app.domain import (CredentialsValidateError, RefreshTokenExpireError,
                        NotFoundError, User)
from app.services.tokens import get_access_token_from_refresh, get_access_token_from_login
from app.services.users import get_password_hash

from app.tests.unit.helpers import get_tokens

log = logging.getLogger(__name__)


def test_check_refresh_token_success(tokens_manager):
    user_id = 2
    refresh_data = {"sub": str(user_id)}
    _, refresh_token = get_tokens(refresh_data=refresh_data)
    tokens_manager.check_refresh_token(refresh_token, user_id)


@pytest.mark.asyncio
async def test_get_access_token_from_refresh_without_register_user(redis_service, manager, tokens_manager):
    user_id = 2
    with pytest.raises(NotFoundError):
        await get_access_token_from_refresh(manager, redis_service, tokens_manager, user_id)


@pytest.mark.asyncio
async def test_get_access_token_from_password_without_register_user(
    redis_service, manager, tokens_manager
):
    user_id = 2
    with pytest.raises(NotFoundError):
        await get_access_token_from_login(redis_service, manager, tokens_manager, "", user_id)


@pytest.mark.asyncio
async def test_get_access_token_from_refresh_success(redis_service, manager, tokens_manager):
    user_id = 2
    user = {"id": user_id, "username": "user", "password": "password", "salt": "salt"}
    await manager.create(User, **user)
    refresh_data = {"sub": str(user_id)}
    _, refresh_token = get_tokens(refresh_data=refresh_data)
    await redis_service.set(f"{user_id}:refresh_key", refresh_token)
    access_token = await get_access_token_from_refresh(manager, redis_service, tokens_manager, user_id)
    data = tokens_manager.get_payload(access_token)
    assert data["sub"] == str(user_id)
    assert data["type"] == "access"
    #assert data["roles"] == ["admin"]


@pytest.mark.asyncio
async def test_get_access_token_from_refresh_fail(redis_service, manager, tokens_manager):
    user_id = 2
    user = {"id": user_id, "username": "user", "password": "password", "salt": "salt"}
    await manager.create(User, **user)
    with pytest.raises(RefreshTokenExpireError):
        await get_access_token_from_refresh(manager, redis_service, tokens_manager, user_id)


@pytest.mark.asyncio
async def test_get_access_token_from_password_success(redis_service, manager, tokens_manager):
    user_id = 2
    password = "password"
    hash_password = get_password_hash(password)
    user = {
        "id": user_id,
        "username": "user",
        "password": hash_password,
        "salt": "salt",
    }
    await manager.create(User, **user)
    access_token = await get_access_token_from_login(
        redis_service, manager, tokens_manager, password, user_id
    )
    data = tokens_manager.get_payload(access_token)
    assert data["sub"] == str(user_id)
    assert data["type"] == "access"
    #assert data["roles"] == ["admin"]


@pytest.mark.asyncio
async def test_get_access_token_from_password_with_wrong_password(redis_service, manager, tokens_manager):
    user_id = 2
    password = "password"
    hash_password = get_password_hash(password)
    user = {
        "id": user_id,
        "username": "user",
        "password": hash_password,
        "salt": "salt",
    }
    await manager.create(User, **user)
    wrong_password = "wrong_password"
    with pytest.raises(CredentialsValidateError):
        await get_access_token_from_login(
            redis_service, manager, tokens_manager, wrong_password, user_id
        )
