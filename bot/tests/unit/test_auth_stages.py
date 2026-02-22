import logging

import pytest

from bot.services import AuthStage
from bot.services.auth import ensure_auth, action_with_unlock_storage
from bot.services.exceptions import AuthError

from bot.tests.unit.conftest import fake_redis, get_fake_http_client

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_ensure_auth_need_registration(get_fake_http_client, fake_redis):
    http_client = get_fake_http_client()
    with pytest.raises(AuthError) as exc:
        user_id = 1
        await ensure_auth(http_client, fake_redis, user_id)
    exc_info = exc.value
    assert exc_info.status == AuthStage.NEED_REGISTRATION


@pytest.mark.asyncio
async def test_ensure_auth_need_login_without_password(
    get_fake_http_client, fake_redis
):
    http_client = get_fake_http_client(False)
    with pytest.raises(AuthError) as exc:
        user_id = 1
        await ensure_auth(http_client, fake_redis, user_id)
    exc_info = exc.value
    assert exc_info.status == AuthStage.NEED_PASSWORD


@pytest.mark.asyncio
async def test_ensure_auth_need_login_with_wrong_password(
    get_fake_http_client, fake_redis
):
    http_client = get_fake_http_client(False)
    with pytest.raises(AuthError) as exc:
        user_id, user_password = 1, "password"
        await ensure_auth(http_client, fake_redis, user_id, user_password)
    exc_info = exc.value
    assert exc_info.status == AuthStage.WRONG_PASSWORD


@pytest.mark.asyncio
async def test_ensure_auth_need_unlock_with_wrong_password(
    get_fake_http_client, fake_redis
):
    http_client = get_fake_http_client(False)
    with pytest.raises(AuthError) as exc:
        await action_with_unlock_storage(http_client.create_account, user_id=1, password="", http_client=http_client)
    exc_info = exc.value
    assert exc_info.status == AuthStage.WRONG_PASSWORD


@pytest.mark.asyncio
async def test_ensure_auth_need_unlock_without_password(
    get_fake_http_client, fake_redis
):
    http_client = get_fake_http_client(False)
    with pytest.raises(AuthError) as exc:
        await action_with_unlock_storage(http_client.create_account, user_id=1)
    exc_info = exc.value
    assert exc_info.status == AuthStage.NEED_UNLOCK

