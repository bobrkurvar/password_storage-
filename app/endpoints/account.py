from fastapi import APIRouter, status
from core.security import getUserFromTokenDep
from db import DbManagerDep
from db.models import Account
from app.endpoints.schemas.account import AccInput
from app.exceptions.custom_errors import CustomDbException
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.get('')
async def accounts_list(user_id: getUserFromTokenDep, manager: DbManagerDep):
    acc_lst = await manager.read(model=Account, ident='user_id', ident_val=int(user_id))
    if acc_lst is None:
        raise CustomDbException(message='список задач пуст', detail='в базе нет ни одной задачи',
                                status_code=status.HTTP_404_NOT_FOUND)
    return acc_lst

@router.post('')
async def create_account(acc: AccInput, manager: DbManagerDep, user_id: getUserFromTokenDep):
    try:
        await manager.create(model=Account, **acc.model_dump())
    except IntegrityError:
        raise CustomDbException(message='ошибка целостности бд', detail='аккаунт с данным id уже существует',
                                status_code=status.HTTP_200_OK)
    return acc.resource



