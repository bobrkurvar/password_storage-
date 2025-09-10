from typing import Annotated

from fastapi import Depends

from core import *

from .crud import Crud


def get_db_manager() -> Crud:
    db_url = conf.db_url
    return Crud(db_url)


DbManagerDep = Annotated[Crud, Depends(get_db_manager)]
