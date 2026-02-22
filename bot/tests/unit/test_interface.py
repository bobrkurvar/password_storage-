import logging

import pytest

from bot.services.auth import (action_with_unlock_storage, ensure_auth,
                               match_status_and_interface)
from bot.services.exceptions import AuthError
from bot.texts import phrases

from bot.tests.unit.conftest import fake_redis, get_fake_http_client

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_match_interface_need_registration(get_fake_http_client, fake_redis):
    http_client = get_fake_http_client()
    with pytest.raises(AuthError):
        _, status = await ensure_auth(http_client, fake_redis, 1)
        text, buttons = match_status_and_interface(status)
        assert text == phrases.need_register and buttons == ("MENU",)


@pytest.mark.asyncio
async def test_match_interface_need_login_with_wrong_password(
    get_fake_http_client, fake_redis
):
    http_client = get_fake_http_client()
    with pytest.raises(AuthError):
        _, status = await ensure_auth(http_client, fake_redis, 1)
        text, buttons = match_status_and_interface(status)
        assert text == phrases.wrong_password and buttons == ("MENU",)


@pytest.mark.asyncio
async def test_match_interface_need_login_without_password(
    get_fake_http_client, fake_redis
):
    http_client = get_fake_http_client()
    with pytest.raises(AuthError):
        _, status = await ensure_auth(http_client, fake_redis, 1)
        text, buttons = match_status_and_interface(status)
        assert text == phrases.login and buttons == ("MENU",)


@pytest.mark.asyncio
async def test_match_interface_need_unlock_without_password(
    get_fake_http_client, fake_redis
):
    http_client = get_fake_http_client()
    with pytest.raises(AuthError):
        _, status = await action_with_unlock_storage(
            http_client.create_account, user_id=1
        )
        text, buttons = match_status_and_interface(status)
        assert text == phrases.need_unlock and buttons == ("MENU",)


@pytest.mark.asyncio
async def test_match_interface_need_unlock_with_wrong_password(
    get_fake_http_client, fake_redis
):
    http_client = get_fake_http_client(password=True)
    with pytest.raises(AuthError):
        _, status = await action_with_unlock_storage(
            http_client.create_account, user_id=1
        )
        text, buttons = match_status_and_interface(status)
        assert text == phrases.wrong_password and buttons == ("MENU",)
