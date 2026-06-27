import logging

from app.dto.account import CreateAccountDto, CreateAccountDto

from app.infra.security import encrypt_account_content, decrypt_account_content
from .users import get_dek_from_redis_or_password

log = logging.getLogger(__name__)


async def create_account(
    uow,
    redis_service,
    account: CreateAccountDto,
    user_id: int,
    user_password: str | None = None,
):
    dek = await get_dek_from_redis_or_password(
        redis_service, uow, user_id, user_password
    )
    if dek:
        for key, value in account.secret_data.items():
            account.secret_data[key] = encrypt_account_content(value, dek)
        async with uow:
            return await uow.db.create(account)


async def read_accounts(uow, redis_service, user_id: int, **filters):
    dek = await get_dek_from_redis_or_password(
        redis_service, uow, user_id
    )
    if dek:
        async with uow:
            accounts = await uow.db.read(
                Account,
                user_id=user_id,
                to_join = ["params"],
                **filters
            )
        for account in accounts:
            account["password"] = decrypt_account_content(account["password"], dek)
            for param in account["params"]:
                log.debug("param: %s", param)
                if param["secret"]:
                    param["content"] = decrypt_account_content(param["content"], dek)
        return accounts