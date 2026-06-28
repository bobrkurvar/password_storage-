import logging

from fastapi import APIRouter

from api.schemas import UserForRegistration
from api.schemas import AccountInput
from dto import CreateAccountDto
from services.users import user_registration
from services.account import create_account, read_accounts
from adapters.deps import UowDep, UserForStorageDep

router = APIRouter(prefix="/user")
log = logging.getLogger(__name__)



@router.post("")
async def registration(uow: UowDep, user: UserForRegistration):
    return await user_registration(uow, password=user.password, username=user.username)


@router.post("/accounts")
async def user_create_account(user: UserForStorageDep, uow: UowDep, account: AccountInput):
    account_dto = CreateAccountDto(user_id=user.id, name=account.name, public_data=account.public_data, secret_data=account.secret_data)
    return await create_account(uow=uow, account=account_dto, dek=user.dek)


@router.get("/accounts")
async def user_get_accounts(user: UserForStorageDep, uow: UowDep):
    return await read_accounts(user_id=user.id, dek=user.dek, uow=uow)
