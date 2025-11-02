from fastapi import APIRouter

from . import manage, own

router = APIRouter(tags=["user"])

router.include_router(own.router, prefix="/user")
router.include_router(manage.router, prefix="/user")
