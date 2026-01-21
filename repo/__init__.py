from core import conf

from .crud import Crud


def get_db_manager() -> Crud:
    db_url = conf.db_url
    return Crud(db_url)
