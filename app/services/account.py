import logging

from app.domain.account import Account, Param
from app.services.UoW import UnitOfWork
from .users import get_user_derive_key
from .security import encrypt_account_content

log = logging.getLogger(__name__)


async def create_account(manager, redis_service, name: str, user_id: int, password: str, params: list, user_password: str | None = None):
    master_key = await get_user_derive_key(redis_service, manager, user_id, user_password)
    if master_key:
        async with UnitOfWork(manager._session_factory) as uow:
            password = encrypt_account_content(password, master_key)
            account = await manager.create(
                Account, name=name, user_id=user_id, password=password, session=uow.session
            )
            log.debug("ACCOUNT ID: %s", account["id"])
            for param in params:
                if param["secret"]:
                    param["content"] = encrypt_account_content(param["content"], master_key)
                param.update(account_id=account["id"])
                await manager.create(Param, session=uow.session, **param)

            return account, params


async def read_accounts(manager, redis_service):
    pass