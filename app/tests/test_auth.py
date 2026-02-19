import pytest
from .conftests import get_tokens
from app.services.tokens import check_refresh_token
from app.domain.exceptions import UnauthorizedError

@pytest.mark.asyncio
async def test_check_refresh_token_success(get_tokens):
    user_id = 2
    access_data = {"sub": user_id, "type": "access"}
    refresh_data = {"sub": user_id, "type": "refresh"}
    _, refresh_token = get_tokens(access_data=access_data, refresh_data=refresh_data)
    await check_refresh_token(refresh_token, user_id)
    assert True

@pytest.mark.asyncio
async def test_check_refresh_token_fail_type(get_tokens):
    user_id = 2
    access_data = {"sub": user_id, "type": "access"}
    refresh_data = {"sub": user_id}
    _, refresh_token = get_tokens(access_data=access_data, refresh_data=refresh_data)
    with pytest.raises(UnauthorizedError):
        await check_refresh_token(refresh_token, user_id)
    assert True


