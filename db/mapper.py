from app.db import models
from sqlalchemy import inspect





class MapperRegistry:
    def __init__(self):
        self._models = {}  # domain_cls -> orm_model
        self._to_orm_funcs = {}  # domain_cls -> func
        self._to_domain_funcs = {}  # orm_model -> func (Внимание: ключ - ORM класс!)

    def register(self, domain_cls, orm_model, to_orm, to_domain):
        self._models[domain_cls] = orm_model
        self._to_orm_funcs[domain_cls] = to_orm
        self._to_domain_funcs[orm_model] = to_domain

    def get_model(self, domain_cls):
        return self._models[domain_cls]

    def to_orm(self, domain_obj):
        domain_cls = type(domain_obj)
        func = self._to_orm_funcs.get(domain_cls)
        if not func:
            raise RuntimeError(f"Маппер в ORM не найден для {domain_cls}")
        return func(domain_obj)

    def to_dto(self, orm_obj):
        orm_cls = type(orm_obj)
        func = self._to_domain_funcs.get(orm_cls)
        if not func:
            raise RuntimeError(f"Маппер в Домен не найден для {orm_cls}")
        return func(orm_obj)


registry = MapperRegistry()


