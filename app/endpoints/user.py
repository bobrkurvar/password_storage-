from fastapi import APIRouter, status
from app.endpoints.schemas.user import UserInput
from sqlalchemy.exc import IntegrityError
from app.exceptions.custom_errors import CustomDbException
from db import DbManagerDep
from db.models import User
import logging


router = APIRouter(tags=['User',])
log = logging.getLogger(__name__)

@router.post('', status_code=status.HTTP_201_CREATED, summary='создание пользователя')
async def user_register(user: UserInput, manager: DbManagerDep):
    try:
        user_id = await manager.create(model=User, **user.model_dump())
    except IntegrityError:
        raise CustomDbException(message='ошибка целостности бд', detail='пользователь с данным id уже существует',
                                status_code=status.HTTP_200_OK)
    return user_id

@router.get('/{_id}', status_code=status.HTTP_200_OK, summary='чтение пользователя')
async def get_user(_id: int, manager: DbManagerDep):
    user = await manager.read(model=User, ident='id', ident_val=_id)
    if user is None:
        raise CustomDbException(message='пользователь с таким id не существует', detail=f'пользователя с id {_id} нет в базе',
                                status_code=status.HTTP_404_NOT_FOUND)
    return user

@router.delete('/{_id}', status_code=status.HTTP_200_OK, summary='удаление пользователя')
async def delete_user(_id: int, manager: DbManagerDep):
     return await manager.delete(model=User, ident_val=_id)









