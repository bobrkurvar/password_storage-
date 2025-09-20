import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.endpoints.schemas.user import UserInput, UserOutput
from app.exceptions.schemas import ErrorResponse
from db import DbManagerDep
from db.models import User

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
    try:
        await manager.create(model=User, **user.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким id уже существует",
        )
    return user


@router.get(
    "/{_id}",
    status_code=status.HTTP_200_OK,
    summary="Получения пользователя по id",
    response_model=UserOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Пользователь не найден",
            "model": ErrorResponse,
        }
    },
)
async def read_user_by_id(_id: int, manager: dbManagerDep):
    user = await manager.read(model=User, ident="id", ident_val=_id)
    log.debug("Пользователь получен %s, %s", user.get("id"), user.get("username"))
    return user

@router.get('',
            summary='Получение пользователей по username или всего списка',
            response_model=UserOutput,
            status_code=status.HTTP_200_OK,
            responses={
                status.HTTP_404_NOT_FOUND: {
                    'detail': 'Пользователи с таким username не найдены или список пуст',
                    'model': ErrorResponse
                }
            }
)
async def read_users_by_criteria(manager: dbManagerDep, username: str | None = None):
    if username is None:
        res = await manager.


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
async def delete_user(_id: int, manager: DbManagerDep):
    user = await manager.delete(model=User, ident_val=_id)[0]
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="пользователь с таким id не существует",
        )
    return user
