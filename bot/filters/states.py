from aiogram.fsm.state import StatesGroup, State


class InputUser(StatesGroup):
    user = State()
    new_password = State()
    password = State()

class InputAccount(StatesGroup):
    name = State()
    password = State()