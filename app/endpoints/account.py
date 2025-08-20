from fastapi import APIRouter
from core.security import getUserFromTokenDep
from db import DbManagerDep
from db.models import Account
from app.endpoints.schemas.account import AccInput

router = APIRouter()

@router.get('/list')
async def accounts_list(user_id: getUserFromTokenDep, manager: DbManagerDep):
    acc_lst = await manager.read(model=Account, ident='user_id', ident_val=user_id)
    return acc_lst

@router.post('/create')
async def create_account(acc: AccInput, manager: DbManagerDep, user_id: getUserFromTokenDep):
    res = await manager.create(model=Account, **acc.model_dump())
    return res.get('resource')



