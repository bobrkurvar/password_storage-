from app.domain import Account, Param, User, Role, UserRole, Admin


class DomainToOrmMapper:
    domain_model_to_orm_fields_mapper = {
        User: (
            "id",
            "username",
            "password",
            "salt",
        ),
        Account: (
            "id",
            "user_id",
            "password",
        ),
        Param: (
            "id",
            "account_id",
            "name",
            "secret",
            "content",
        ),
        Role: ("role_name",),
        UserRole: (
            "user_id",
            "role_name",
        ),
        Admin: ("id",),
    }

    @classmethod
    def fields(cls, domain_model):
        return cls.domain_model_to_orm_fields_mapper[domain_model]
