from fastapi import APIRouter, status
from core.security import create_access_token, verify
from app.endpoints.schemas.user import UserInput
from sqlalchemy.exc import IntegrityError
from app.exceptions.custom_errors import CustomDbException
from db import DbManagerDep
from db.models import User

router = APIRouter()

@router.post('/create', status_code=status.HTTP_201_CREATED, summary='создание пользователя')
async def user_register(user: UserInput, manager: DbManagerDep):
    try:
        user_id = await manager.create(model=User, **user.model_dump())
    except IntegrityError:
        raise CustomDbException(message='ошибка целостности бд', detail='пользователь с данным id уже существует',
                                status_code=status.HTTP_200_OK)
    return user_id

@router.get('/{_id}', status_code=status.HTTP_200_OK, summary='чтение пользователя')
async def get_user(_id: int, manager: DbManagerDep):
    user = await manager.read(model=User, ident='id', idenv_val=_id)
    return user

@router.post('/login', status_code=status.HTTP_200_OK, summary='аутентификация пользователя')
async def login_user(user: UserInput, manager: DbManagerDep):
    cur = await manager.read(model=User, ident='id', ident_val=user.id)
    if verify(user.password, cur.get('password')):
        token = create_access_token({'sub': str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
    return {'error': 'User not fount'}





