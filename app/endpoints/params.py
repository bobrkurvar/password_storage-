from fastapi import APIRouter, status, Depends
from core.security import get_user_from_token
from db.models import ParOfAcc
from app.endpoints.schemas.account import ParamsInput
from db import DbManagerDep
from typing import Optional

router = APIRouter(tags=["Params of account"])


@router.get(
    "{id_}",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="чтение параметра по id",
)
async def get_param_by_id(id_: int, manager: DbManagerDep):
    param = (await manager.read(model=ParOfAcc, ident_val=id_))[0]
    return param


@router.get(
    "",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="чтение параметров по критериям поиска",
)
async def get_param_by_id(
    ident: str,
    ident_val: Optional[int | str],
    manager: DbManagerDep,
    to_join: str | None = None,
):
    params = await manager.read(
        model=ParOfAcc, ident=ident, ident_val=int(ident_val), to_join=to_join
    )
    return params


@router.post(
    "",
    dependencies=[Depends(get_user_from_token)],
    status_code=status.HTTP_200_OK,
    summary="создание параметров для аккаунта",
)
async def create_account_params(items: ParamsInput, manager: DbManagerDep):
    for param in items.items:
        param.update(acc_id=items.acc_id)
        await manager.create(model=ParOfAcc, **param)
