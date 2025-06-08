from fastapi import APIRouter
from core.security import create_token, verify, get_password_hash
from web.endpoints.schemas.user import UserInput, OutputUser
from db import manager
from db.models import User

router = APIRouter()

@router.post('/create', response_model=OutputUser)
async def user_register(user: UserInput):
    print(user.model_dump())
    user_id = await manager.create(model=User, **user.model_dump())
    return user_id

@router.get('/read')
async def get_user(id: int):
    user = await manager.read(model=User, id=id)
    return user

@router.post('/login')
async def login_user(user: UserInput):
    cur = await manager.read(model=User, id=user.id)
    print(cur)
    if verify(user.password, cur.get('password')):
        token = create_token({'sub': str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
    return {'error': 'User not fount'}


