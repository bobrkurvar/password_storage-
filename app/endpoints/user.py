import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.endpoints.schemas.user import (UserInput, UserOutput, UserRolesInput,
                                        UserRolesOutput)
from app.exceptions.schemas import ErrorResponse
from db import Crud, get_db_manager
from db.models import Roles, Users, UsersRoles

router = APIRouter(
    tags=["User"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "detail": "Unexpected error",
            "model": ErrorResponse,
        },
    },
)
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
    return res


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


@router.get(
    "/{_id}/roles",
    status_code=status.HTTP_200_OK,
    summary="Чтение ролей пользователя по id",
    response_model=list[UserRolesOutput],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "У пользователя нет ролей",
            "model": ErrorResponse,
        }
    },
)
async def read_user_roles(_id: int, manager: dbManagerDep):
    result = await manager.read(
        model=Roles, ident="user_id", ident_val=_id, to_join="users_roles"
    )
    return result


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
    "",
    summary="Получение пользователя по username или всего списка",
    status_code=status.HTTP_200_OK,
    response_model=list[UserOutput],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Пользователи не найдены или список пуст",
            "model": ErrorResponse,
        }
    },
)
async def read_user_by_criteria_or_full_list(
    manager: dbManagerDep, username: str | None = None
):
    if username is None:
        log.debug("Запрос на чтение списка пользователей")
        res = await manager.read(Users)
    else:
        res = await manager.read(Users, ident="username", ident_val=username)
    return res


@router.delete(
    "/{_id}",
    status_code=status.HTTP_200_OK,
    summary="удаление пользователя",
    response_model=UserOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Пользователь не найден",
            "model": ErrorResponse,
        }
    },
)
async def delete_user(_id: int, manager: dbManagerDep):
    user = await manager.delete(model=Users, ident_val=_id)
    return user


@router.post(
    "/{user_id}/roles",
    status_code=status.HTTP_201_CREATED,
    summary="создание роли пользователя",
    response_model=UserRolesOutput,
    responses={
        status.HTTP_409_CONFLICT: {
            "detail": "Роль с таким id или именем уже существует",
            "model": ErrorResponse,
        }
    },
)
async def create_user_role(user_id: int, role: UserRolesInput, manager: dbManagerDep):
    result = await manager.create(
        model=UsersRoles, user_id=user_id, role_id=role.role_id
    )
    log.debug("result: %s", result)
    return {"role_id": role.role_id, "role_name": role.role_name}
