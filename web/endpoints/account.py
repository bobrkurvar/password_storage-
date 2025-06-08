from fastapi import APIRouter
from core.security import getUserFromTokenDep
from db import manager
from db.models import Account
from web.endpoints.schemas.account import AccInput

router = APIRouter()

@router.get('/list')
async def accounts_list(user_id: getUserFromTokenDep):
    acc_lst = await manager.read(model=Account, ident={'user_id': user_id})
    return acc_lst

@router.post('/create')
async def create_account(acc: AccInput, user: getUserFromTokenDep):
    res = await manager.create(model=Account, **acc.model_dump())
    print(50*'-', f'создан {res}', 50*'-', sep='\n')
    return res.get('resource')



