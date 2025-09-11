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
async def user_create(user: UserInput, manager: DbManagerDep):
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
    summary="чтение пользователя",
    response_model=UserOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Пользователь не найден",
            "model": ErrorResponse,
        }
    },
)
async def get_user(_id: int, manager: DbManagerDep):
    user = (await manager.read(model=User, ident="id", ident_val=_id))[0]
    log.debug('Пользователь получен %s, %s', user.get('id'), user.get('username'))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="пользователь с таким id не существует",
        )
    return user


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
