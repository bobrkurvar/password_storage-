from aiogram.filters.callback_data import CallbackData


class CallbackFactory(CallbackData, prefix="pas"):
    #user_id: int | None = None
    #password: str | None = None
    #account_id: int | None = None
    act: str | None = None
