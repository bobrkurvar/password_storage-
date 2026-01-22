from core import conf
import domain
from db import models
from .crud import Crud


def get_db_manager() -> Crud:
    db_url = conf.db_url
    domain_with_orm = {
        domain.User: models.User,
        domain.UserRole: models.UserRole,
        domain.Role: models.Role,
        domain.Account: models.Account,
        domain.Param: models.Param,
        domain.Admin: models.Admin,
    }
    return Crud(db_url, domain_with_orm)
