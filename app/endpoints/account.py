from fastapi import APIRouter, status, Depends
from core.security import getUserFromTokenDep, get_user_from_token
from db import DbManagerDep
from db.models import Account
from app.endpoints.schemas.account import AccInput, AccUpdate
from app.exceptions.custom_errors import CustomDbException
from sqlalchemy.exc import IntegrityError
from typing import Optional
import logging


router = APIRouter(tags=['Account',])
log = logging.getLogger(__name__)

@router.get('{id_}', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_200_OK, summary='получение одного аккаунта')
async def account_by_id(id_: int, manager: DbManagerDep):
    account = await manager.read(model=Account, ident=id_)
    return account

@router.get('', status_code=status.HTTP_200_OK, summary='получение списка аккаунтов')
async def accounts_list(user_id: getUserFromTokenDep, manager: DbManagerDep):
    acc_lst = await manager.read(model=Account, ident='user_id', ident_val=int(user_id))
    if acc_lst is None:
        raise CustomDbException(message='список задач пуст', detail='в базе нет ни одной задачи',
                                status_code=status.HTTP_404_NOT_FOUND)
    return acc_lst

@router.post('', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_201_CREATED, summary='создание аккаунта')
async def create_account(acc: AccInput, manager: DbManagerDep):
    try:
        acc_id = await manager.create(model=Account, **acc.model_dump())
        log.debug('returning acc_id: %s', acc_id)
    except IntegrityError:
        raise CustomDbException(message='ошибка целостности бд', detail='аккаунт с данным id уже существует',
                                status_code=status.HTTP_200_OK)
    return acc_id

@router.delete('', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_200_OK,
               summary='удаление всех аккаунтов')
async def delete_all_accounts(manager: DbManagerDep):
    await manager.delete(model=Account)

@router.delete('{id_}', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_200_OK,
               summary='удаление одного аккаунта')
async def delete_account_by_id(id_: int, manager: DbManagerDep):
    await manager.delete(model=Account, ident=id_)
    return id_

@router.delete('', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_200_OK,
               summary='удаление аккунтов по критерию поиска')
async def delete_account_by_criteria(ident: str, ident_val: Optional[int], manager: DbManagerDep):
    await manager.delete(model=Account, ident=ident, ident_val=ident_val)


@router.patch('{id_}', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_200_OK,
              summary='изменения аккаунта по id')
async def change_account_by_id(id_: int, acc: AccUpdate, manager: DbManagerDep):
    to_update = dict()
    if not (acc.resource is None):
        to_update.update(resource=acc.resource)
    if not (AccUpdate.password is None):
        to_update.update(password=acc.password)
    if to_update:
        await manager.update(model=Account, **to_update, ident_val=id_)

@router.patch('', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_200_OK,
              summary='изменение аккаунтов по критериям поиска')
async def change_account_by_criteria(ident: str, ident_val: Optional[int],
                                     acc: AccUpdate, manager: DbManagerDep):
    to_update = dict()
    if not (acc.resource is None):
        to_update.update(resource=acc.resource)
    if not (AccUpdate.password is None):
        to_update.update(password=acc.password)
    if to_update:
        await manager.update(model=Account, **to_update, ident=ident, ident_val=ident_val)



