import logging

from app.domain.account import Account, Param
from app.services.UoW import UnitOfWork

log = logging.getLogger(__name__)


async def create_account(manager, name: str, user_id: int, password: str, params: list):
    async with UnitOfWork(manager._session_factory) as uow:
        account = await manager.create(
            Account, name=name, user_id=user_id, password=password, session=uow.session
        )
        log.debug("ACCOUNT ID: %s", account["id"])
        for param in params:
            param.update(account_id=account["id"])
            await manager.create(Param, session=uow.session, **param)

        return account, params
