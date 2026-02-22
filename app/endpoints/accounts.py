import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.auth import get_user_from_token, getUserFromTokenDep
from app.adapters.crud import Crud, get_db_manager
from app.endpoints.schemas.account import AccountInput
from app.services.account import create_account, read_accounts
from shared.adapters.redis import RedisService, get_redis_service

router = APIRouter(
    prefix="/accounts",
    tags=["own"],
    dependencies=[Depends(get_user_from_token)],
)
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
redisServiceDep = Annotated[RedisService, Depends(get_redis_service)]

@router.get("")
async def user_accounts_list(user: getUserFromTokenDep, manager: dbManagerDep, redis_service: redisServiceDep):
    log.debug(f"получение списка аккаунтов для пользователя с {user.get('user_id')}")
    return await read_accounts(manager, redis_service, user_id=int(user.get("user_id")))


@router.post("")
async def create_account_with_params(
    user: getUserFromTokenDep, account: AccountInput, manager: dbManagerDep, redis_service: redisServiceDep
):
    created_account, params = await create_account(
        manager, redis_service, **account.model_dump(), user_id=user["user_id"]
    )
    if created_account is None:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    return created_account
