from aiogram.filters.callback_data import CallbackData

class CallbackPasswordFactory(CallbackData, prefix='pas'):
    id: int | None = None
    user_id: int
    password: str | None = None
    resource_id: int | None = None
    account_id: int | None = None
    act: str
