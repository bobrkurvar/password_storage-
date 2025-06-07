from fastapi import APIRouter
from core.security import create_token
from web.endpoints.schemas.user import UserInput, OutputUser
from db import manager
from db.models import User

router = APIRouter()

@router.post('/create', response_model=OutputUser)
async def user_register(user: UserInput):
    print(user.model_dump())
    user_id = await manager.create(model=User, **user.model_dump())
    return user_id

@router.get('/login')
async def login_user(user: UserInput):
    if await manager.read(model=User, ident=user.model_dump()):
        token = create_token({'sub': user.id})
        return {"access_token": token, "token_type": "bearer"}
    return {'error': 'User not fount'}


