import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException

from app.adapters.auth import get_user_from_token, getUserFromTokenDep
from app.adapters.crud import Crud, get_db_manager
from app.domain import Account, NotFoundError
from app.endpoints.schemas.account import AccountInputFromUser, AccountOutput
from app.endpoints.schemas.errors import ErrorResponse
from app.services.account import create_account

router = APIRouter(
    prefix="/account",
    tags=["own"],
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
    dependencies=[Depends(get_user_from_token)],
)
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получение списка аккаунтов по id владельца полученного из токена",
    response_model=list[AccountOutput],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Список задач пуст",
            "model": ErrorResponse,
        }
    },
)
async def user_accounts_list(user: getUserFromTokenDep, manager: dbManagerDep):
    log.debug(f"получение списка аккаунтов для пользователя с {user.get('user_id')}")
    acc_lst = await manager.read(
        Account, ident="user_id", ident_val=int(user.get("user_id"))
    )
    return acc_lst


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создание аккаунта",
    response_model=AccountOutput,
    responses={
        status.HTTP_409_CONFLICT: {
            "detail": "Аккаунт с данным id уже существует",
            "model": ErrorResponse,
        }
    },
)
async def create_account_with_params(
    user: getUserFromTokenDep, account: AccountInputFromUser, manager: dbManagerDep
):
    created_account, params = await create_account(
        manager, **account.model_dump(), user_id=user["user_id"]
    )
    if created_account is None:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    return created_account
