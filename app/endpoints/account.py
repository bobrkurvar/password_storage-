import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.endpoints.schemas.account import AccInput, AccOutput, AccUpdate
from app.exceptions.schemas import ErrorResponse
from core.security import get_user_from_token, getUserFromTokenDep
from db import Crud, get_db_manager
from db.models import Account, ParOfAcc

router = APIRouter(
    tags=["Account"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "detail": "Unexpected error",
            "model": ErrorResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "detail": "Unauthorized error",
            "model": ErrorResponse,
        },
    },
)
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.get(
    "{id_}",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="получение одного аккаунта",
    response_model=AccOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Аккаунт не найден",
            "model": ErrorResponse,
        }
    },
)
async def account_by_id(id_: int, manager: dbManagerDep):
    account = await manager.read(model=Account, ident=id_)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Аккаунт не найден"
        )
    return account


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получение списка аккаунтов",
    response_model=List[AccOutput],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Список задач пуст",
            "model": ErrorResponse,
        }
    },
)
async def accounts_list(user_id: getUserFromTokenDep, manager: dbManagerDep):
    acc_lst = await manager.read(model=Account, ident="user_id", ident_val=int(user_id))
    if acc_lst is None:
        raise HTTPException(
            detail="Список задач пуст", status_code=status.HTTP_404_NOT_FOUND
        )
    log.debug("accounts list: %s", acc_lst)
    return acc_lst


@router.post(
    "",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_201_CREATED,
    summary="Создание аккаунта",
    response_model=AccOutput,
    responses={
        status.HTTP_409_CONFLICT: {
            "detail": "Аккаунт с данным id уже существует",
            "model": ErrorResponse,
        }
    },
)
async def create_account(acc: AccInput, manager: dbManagerDep):
    try:
        acc_from_db = await manager.create(model=Account, **acc.model_dump())
        log.debug(
            "returning acc: %s, %s", acc_from_db.get("id"), acc_from_db.get("user_id")
        )
    except IntegrityError:
        raise HTTPException(
            detail="Аккаунт с данным id уже существует",
            status_code=status.HTTP_409_CONFLICT,
        )
    return acc_from_db


@router.delete(
    "",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="Удаление всех аккаунтов",
    response_model=AccOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Список аккаунтов пуст",
            "model": ErrorResponse,
        }
    },
)
async def delete_all_accounts(manager: dbManagerDep):
    acc = await manager.delete(model=Account)
    if acc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Список аккаунтов пуст"
        )
    # return acc


@router.delete(
    "{id_}",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="Удаление одного аккаунта",
    response_model=AccOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Аккаунт не найден",
            "model": ErrorResponse,
        }
    },
)
async def delete_account_by_id(id_: int, manager: dbManagerDep):
    acc = await manager.delete(model=Account, ident=id_)
    if acc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Аккаунт не найден"
        )
    return acc


@router.delete(
    "",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="удаление аккаунтов по критерию поиска",
    response_model=AccOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Аккаунт с таким критерием не найден",
            "model": ErrorResponse,
        }
    },
)
async def delete_account_by_criteria(
    ident: str, ident_val: int | None, manager: dbManagerDep
):
    acc = await manager.delete(model=Account, ident=ident, ident_val=ident_val)
    if acc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Аккаунт с таким {ident} не найден",
        )
    return acc


# @router.patch('{id_}',
#               dependencies=[Depends(get_user_from_token)],
#               status_code=status.HTTP_204_NO_CONTENT,
#               summary='Изменение аккаунта по id',
# )
# async def change_account_by_id(id_: int, acc: AccUpdate, manager: DbManagerDep):
#     to_update = dict()
#     if not (acc.resource is None):
#         to_update.update(resource=acc.resource)
#     if not (AccUpdate.password is None):
#         to_update.update(password=acc.password)
#     if to_update:
#         await manager.update(model=Account, **to_update, ident_val=id_)
#
# @router.patch('', dependencies=[Depends(get_user_from_token)], status_code=status.HTTP_200_OK,
#               summary='изменение аккаунтов по критериям поиска')
# async def change_account_by_criteria(ident: str, ident_val: int | None,
#                                      acc: AccUpdate, manager: DbManagerDep):
#     to_update = dict()
#     if not (acc.resource is None):
#         to_update.update(resource=acc.resource)
#     if not (AccUpdate.password is None):
#         to_update.update(password=acc.password)
#     if to_update:
#         await manager.update(model=Account, **to_update, ident=ident, ident_val=ident_val)


@router.get("/load-csv")
async def get_csv_file(
    user_id: getUserFromTokenDep,
    ident: str,
    ident_val: int | str | None,
    manager: dbManagerDep,
    to_join: str | None = None,
):
    params = await manager.read(
        model=ParOfAcc, ident=ident, ident_val=int(ident_val), to_join=to_join
    )
