from fastapi import APIRouter, status
from core.security import create_access_token, verify
from app.endpoints.schemas.user import UserInput, OutputUser
from db import DbManagerDep
from db.models import User

router = APIRouter()

@router.post('/create', response_model=OutputUser, status_code=status.HTTP_201_CREATED, summary='создание пользователя')
async def user_register(user: UserInput, manager: DbManagerDep):
    print(user.model_dump())
    user_id = await manager.create(model=User, **user.model_dump())
    return user_id

@router.get('/read/{_id}', status_code=status.HTTP_200_OK, summary='чтение пользователя')
async def get_user(_id: int, manager: DbManagerDep):
    user = await manager.read(model=User, id=_id)
    return user

@router.post('/login', status_code=status.HTTP_200_OK, summary='аутентификация пользователя')
async def login_user(user: UserInput, manager: DbManagerDep):
    cur = await manager.read(model=User, ident='id', ident_val=user.id)
    if verify(user.password, cur.get('password')):
        token = create_access_token({'sub': str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
    return {'error': 'User not fount'}
#
# @router.get('/refresh', status_code=status.HTTP_200_OK, summary='обновление токена')
# async def refresh_token(rt: str):




