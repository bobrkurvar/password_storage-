import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from app.endpoints.schemas.account import ParamInput, ParamOutput
from app.exceptions.schemas import ErrorResponse
from core.security import get_user_from_token
from db import Crud, get_db_manager
from db.models import Params

router = APIRouter(tags=["Params of account"])
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.get(
    "",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="Чтение параметров по критериям поиска",
    response_model=List[ParamOutput],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Параметров с таким критерием нет",
            "model": ErrorResponse,
        }
    },
)
async def get_param_by_criteria(
    manager: dbManagerDep,
    ident: str,
    ident_val: str | int | None,
    to_join: str | None = None
):
    params = await manager.read(
        model=Params, ident=ident, ident_val=int(ident_val), to_join=to_join
    )
    return params


@router.get(
    "/{id_}",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="чтение параметра по id",
    response_model=ParamOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Параметра с таким id нет",
            "model": ErrorResponse,
        }
    },
)
async def get_param_by_id(id_: int, manager: dbManagerDep):
    param = (await manager.read(model=Params, ident_val=id_))[0]
    return param

@router.post(
    "",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="Создание параметров для аккаунта",
    response_model=List[ParamOutput],
)
async def create_account_params(manager: dbManagerDep, params: ParamInput):
    params_dict = [item.model_dump() for item in params.items]
    [i.update(acc_id=params.acc_id) for i in params_dict]
    log.debug("params_dict: %s", params_dict)
    response = await manager.create(model=Params, seq_data=params_dict)
    return response

@router.delete(
    "",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление параметров аккаунта"
)
async def delete_account_params_by_account_id(manager: dbManagerDep, account_id: int):
    log.debug("Запрос на удаление параметров аккаунта с id: %s", account_id)
    await manager.delete(model=Params, ident="acc_id", ident_val=account_id)

