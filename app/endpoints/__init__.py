from fastapi import APIRouter
from . import user
from . import account

main_router = APIRouter()
main_router.include_router(user.router, prefix='/user')
main_router.include_router(account.router, prefix='/account')
