import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.endpoints.schemas.account import AccOutput
from app.exceptions.schemas import ErrorResponse
from core.security import make_role_checker
from repo import Crud, get_db_manager
from domain import Account

router = APIRouter(
    tags=["manage"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "detail": "Unexpected error",
            "model": ErrorResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "detail": "Unauthorized error",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {"detail": "Role error", "model": ErrorResponse},
    },
    dependencies=[Depends(make_role_checker(required_role=["admin", "moderator"]))],
)
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    summary="Получение списка всех аккаунтов (только для администратора)",
    response_model=list[AccOutput],
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Недостаточно прав для выполнения запроса",
            "model": ErrorResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Аккаунты не найдены",
            "model": ErrorResponse,
        },
    },
)
async def get_all_accounts(manager: dbManagerDep):
    log.debug(f"админ получает список всех аккаунтов")
    acc_lst = await manager.read(model=Account)
    return acc_lst


@router.get(
    "/{id_}",
    status_code=status.HTTP_200_OK,
    summary="получение аккаунта по id",
    response_model=AccOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Аккаунт не найден",
            "model": ErrorResponse,
        }
    },
)
async def account_by_id(id_: int, manager: dbManagerDep):
    log.debug("чтение аккаунта по id %s", id_)
    account = (await manager.read(model=Account, ident="id", ident_val=id_))[0]
    return account


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
    dependencies=[Depends(make_role_checker(required_role=["admin"]))],
)
async def delete_accounts(
    ident: str | None, ident_val: int | None, manager: dbManagerDep
):
    if ident is None:
        log.debug("ЗАПРОС НА УДАЛЕНИЕ ВСЕХ АККАУНТОВ")
        await manager.delete(model=Account)
    else:
        log.debug("УДАЛЕНИЕ АККАУНТА ПО %s = %s", ident, ident_val)
        await manager.delete(model=Account, ident=ident, ident_val=ident_val)


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
    dependencies=[Depends(make_role_checker(required_role=["admin"]))],
)
async def delete_account_by_id(id_: int, manager: dbManagerDep):
    log.debug("ЗАПРСО НА УДАЛЕНИЕ АККАУНТА С ID: %s", id_)
    acc = await manager.delete(model=Account, ident_val=id_)
    return acc
