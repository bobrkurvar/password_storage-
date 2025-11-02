from fastapi import APIRouter

from . import manage, own

router = APIRouter(tags=["accounts"])

router.include_router(own.router, prefix="/account")
router.include_router(manage.router, prefix="/account")
