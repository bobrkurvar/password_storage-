from aiogram.filters.callback_data import CallbackData

class CallbackPasswordFactory(CallbackData, prefix='pas'):
    user_id: int | None = None
    password: str | None = None
    resource_id: int | None = None
    account_id: int | None = None
    act: str
