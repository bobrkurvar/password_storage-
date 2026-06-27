import logging
from typing import Annotated

from fastapi import APIRouter

from app.endpoints.schemas.user import UserForRegistration
from app.services.users import user_registration
from app.services.account import create_account
from app.adapters.deps import UowDep, RedisDep

router = APIRouter(prefix="/user")
log = logging.getLogger(__name__)



@router.post("")
async def registration(uow: UowDep, user: UserForRegistration):
    return await user_registration(uow, user.user_id, user.password, user.username)


@router.post("/accounts")
async def user_create_account(user, uow: UowDep, redis: RedisDep, account):
    return await create_account(uow=uow, redis_service=redis, account=account)