import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.adapters.auth import make_role_checker
from app.adapters.crud import Crud, get_db_manager
from app.domain import Role, User, UserRole
from app.endpoints.schemas.user import (UserInput, UserOutput, UserRolesInput,
                                        UserRolesOutput)
from app.endpoints.schemas.errors import ErrorResponse

router = APIRouter(
    prefix="/user",
    tags=["manage"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "detail": "Unexpected error",
            "model": ErrorResponse,
        },
    },
    dependencies=[Depends(make_role_checker(required_role=["admin", "moderator"]))],
)
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.get(
    "/{user_id:int}",
    status_code=status.HTTP_200_OK,
    summary="Получение пользователя по",
    response_model=UserOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Пользователь не найден",
            "model": ErrorResponse,
        }
    },
)
async def read_user_by_id(user_id: int, manager: dbManagerDep):
    user = await manager.read(User, id=user_id)
    if user:
        user = user[0]
    log.debug("Пользователь получен %s, %s", user.get("id"), user.get("username"))
    return user


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
    res = await manager.create(User, **user.model_dump())
    log.debug("user: %s", res)
    return res


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
        domain_model=Role,
        ident="user_id",
        ident_val=_id,
        to_join=[
            "users_roles",
        ],
    )
    return result


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
async def read_user_by_username_or_full_list(
    manager: dbManagerDep, username: str | None = None
):
    if username is None:
        log.debug("Запрос на чтение списка пользователей")
        res = await manager.read(domain_model=User)
    else:
        res = await manager.read(
            domain_model=User, ident="username", ident_val=username
        )
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
    user = await manager.delete(domain_model=User, ident_val=_id)
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
        domain_model=UserRole, user_id=user_id, role_id=role.role_id
    )
    log.debug("result: %s", result)
    return {"role_id": role.role_id, "role_name": role.role_name}
