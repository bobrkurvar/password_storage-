from fastapi import APIRouter, status, Depends
from core.security import get_user_from_token
from db.models import ParOfAcc
from app.endpoints.schemas.account import ParamsInput
from db import DbManagerDep

router = APIRouter(tags=['Params of account'])


@router.post('', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_200_OK,
             summary='создание параметров для аккаунта')
async def create_account_params(items: ParamsInput, manager: DbManagerDep):
    for param in items.items:
        param.update(acc_id=items.acc_id)
        await manager.create(model=ParOfAcc, **param)
