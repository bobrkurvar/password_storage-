import pytest
from services import user_registration
from tests.fakes import FakeUoW

@pytest.mark.asyncio
async def tests_user_registration_success(manager):
    username, password, user_id = "username", "password", 12
    await user_registration(manager, user_id=user_id, username=username, password=password, uow_class=FakeUoW)

