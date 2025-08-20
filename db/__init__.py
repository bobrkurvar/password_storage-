from .crud import Crud
from core import *
from typing import Annotated
from fastapi import Depends


def get_db_manager() -> Crud:
    db_url = conf.db_url
    return Crud(db_url)

DbManagerDep = Annotated[Crud, Depends(get_db_manager)]