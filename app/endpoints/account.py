from fastapi import APIRouter, status
from core.security import getUserFromTokenDep
from db import DbManagerDep
from db.models import Account
from app.endpoints.schemas.account import AccInput
from app.exceptions.custom_errors import CustomDbException
from sqlalchemy.exc import IntegrityError

router = APIRouter(tags=['Account',])

@router.get('{id_}', status_code=status.HTTP_200_OK, summary='получение одного аккаунта')
async def account_by_id(id_: int, manager: DbManagerDep, user_id: getUserFromTokenDep):
    account = await manager.read(model=Account, ident=id_)
    return account

@router.get('', status_code=status.HTTP_200_OK, summary='получение списка аккаунтов')
async def accounts_list(user_id: getUserFromTokenDep, manager: DbManagerDep):
    acc_lst = await manager.read(model=Account, ident='user_id', ident_val=int(user_id))
    if acc_lst is None:
        raise CustomDbException(message='список задач пуст', detail='в базе нет ни одной задачи',
                                status_code=status.HTTP_404_NOT_FOUND)
    return acc_lst

@router.post('', status_code=status.HTTP_201_CREATED, summary='создание аккаунта')
async def create_account(acc: AccInput, manager: DbManagerDep, user_id: getUserFromTokenDep):
    try:
        await manager.create(model=Account, **acc.model_dump())
    except IntegrityError:
        raise CustomDbException(message='ошибка целостности бд', detail='аккаунт с данным id уже существует',
                                status_code=status.HTTP_200_OK)
    return acc.resource

@router.delete('', status_code=status.HTTP_200_OK, summary='удаление списка аккаунтов')
async def delete_all_accounts(manager: DbManagerDep, user_id: getUserFromTokenDep):
    await manager.delete(model=Account)

@router.delete('{id_}', status_code=status.HTTP_200_OK, summary='удаление одного аккаунта')
async def delete_account_by_id(id_: int, manager: DbManagerDep, user_id: getUserFromTokenDep):
    await manager.delete(model=Account, ident=id_)
    return id_

