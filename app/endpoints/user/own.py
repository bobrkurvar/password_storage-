import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.endpoints.schemas.user import UserInput, UserOutput, UserRolesOutput
from app.exceptions.schemas import ErrorResponse
from core.security import get_user_from_token
from db import Crud, get_db_manager
from db.models import Roles, Users

router = APIRouter(tags=["own"])
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="создание пользователя",
    response_model=UserOutput,
    responses={
        status.HTTP_409_CONFLICT: {
            "detail": "Пользователь с таким id уже существует",
            "model": ErrorResponse,
        },
    },
)
async def user_create(user: UserInput, manager: dbManagerDep):
    res = await manager.create(model=Users, **user.model_dump())
    log.debug("user: %s", res)
    return res

@router.get(
    "/{_id}",
    status_code=status.HTTP_200_OK,
    summary="Получение пользователя по id",
    response_model=UserOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Пользователь не найден",
            "model": ErrorResponse,
        }
    },
)
async def read_user_by_id(_id: int, manager: dbManagerDep):
    user = (await manager.read(model=Users, ident="id", ident_val=_id))[0]
    log.debug("Пользователь получен %s, %s", user.get("id"), user.get("username"))
    return user

@router.get(
    "/roles",
    status_code=status.HTTP_200_OK,
    summary="Чтение ролей по их имени",
    response_model=list[UserRolesOutput],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Список ролей пуст",
            "model": ErrorResponse,
        }
    },
)
async def read_users_roles(role_name: str, manager: dbManagerDep):
    result = await manager.read(model=Roles, ident="role_name", ident_val=role_name)
    return result
