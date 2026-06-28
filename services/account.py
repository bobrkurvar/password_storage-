import logging

from dto import CreateAccountDto, ReadAccountDto, AccountDto

from infra.security import encrypt_account_content, decrypt_account_content

log = logging.getLogger(__name__)


async def create_account(
    uow,
    account: CreateAccountDto,
    dek: bytes
):
    # dek = await get_dek_from_redis_or_password(
    #     redis_service, uow, account.user_id, user_password
    # )
    for key, value in account.secret_data.items():
        account.secret_data[key] = encrypt_account_content(value, dek)
    async with uow:
        return await uow.db.create(account)


async def read_accounts(
    uow,
    dek: bytes,
    user_id: int,
    **filters,
) -> list[AccountDto]:
    async with uow:
        stored_accounts = await uow.db.read(
            ReadAccountDto,
            user_id=user_id,
            **filters,
        )
    result = []
    for account in stored_accounts:
        decrypted_secret_data = {
            key: decrypt_account_content(value, dek)
            for key, value in account.secret_data.items()
        }
        data = {
            "name": account.name,
            **account.public_data,
            **decrypted_secret_data,
        }
        result.append(
            AccountDto(
                id=account.id,
                user_id=account.user_id,
                data=data,
            )
        )

    return result