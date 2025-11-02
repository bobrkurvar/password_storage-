import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.endpoints.schemas.account import AccInput, AccOutput
from app.exceptions.schemas import ErrorResponse
from core.security import get_user_from_token, getUserFromTokenDep, make_role_checker
from db import Crud, get_db_manager
from db.models import Accounts

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
        status.HTTP_403_FORBIDDEN: {
            "detail": "Role error",
            "model": ErrorResponse
        }
    },
    dependencies=[Depends(make_role_checker(model=Accounts))],
)
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.get(
    "/{id_}",
    status_code=status.HTTP_200_OK,
    summary="получение одного аккаунта",
    response_model=AccOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Аккаунт не найден",
            "model": ErrorResponse,
        }
    },
    dependencies=[Depends(make_role_checker(param="id_", model=Accounts, ident="user_id"))]
)
async def account_by_id(id_: int, manager: dbManagerDep):
    log.debug("чтение аккаунта по id %s", id_)
    account = (await manager.read(model=Accounts, ident='id', ident_val=id_))[0]
    return account


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получение списка аккаунтов",
    response_model=list[AccOutput],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Список задач пуст",
            "model": ErrorResponse,
        }
    },
)
async def accounts_list(user: Annotated[dict, Depends(make_role_checker(model=Accounts, ident="user_id"))],
                        manager: dbManagerDep):
    log.debug(f"получение списка аккаунтов для пользователя с {user.get("user_id")}")
    acc_lst = await manager.read(
        model=Accounts, ident="user_id", ident_val=int(user.get('user_id'))
    )
    return acc_lst


@router.post(
    "",
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
    acc_from_db = await manager.create(model=Accounts, **acc.model_dump())
    log.debug(
        "returning acc: %s, %s", acc_from_db.get("id"), acc_from_db.get("user_id")
    )
    return acc_from_db


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="удаление аккаунтов по критерию поиска",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Аккаунт с таким критерием не найден",
            "model": ErrorResponse,
        }
    },
)
async def delete_accounts(
    ident: str | None, ident_val: int | None, manager: dbManagerDep
):
    if ident is None:
        log.debug("ЗАПРОС НА УДАЛЕНИЕ ВСЕХ АККАУНТОВ")
        await manager.delete(model=Accounts)
    else:
        log.debug("УДАЛЕНИЕ АККАУНТА ПО %s = %s", ident, ident_val)
        await manager.delete(model=Accounts, ident=ident, ident_val=ident_val)


@router.delete(
    "/{id_}",
    status_code=status.HTTP_200_OK,
    summary="Удаление одного аккаунта",
    response_model=AccOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Аккаунт не найден",
            "model": ErrorResponse,
        }
    },
    dependencies=[Depends(make_role_checker(model=Accounts, ident="user_id"))]
)
async def delete_account_by_id(id_: int, manager: dbManagerDep):
    log.debug("ЗАПРСО НА УДАЛЕНИЕ АККАУНТА С ID: %s", id_)
    acc = await manager.delete(model=Accounts, ident_val=id_)
    return acc
