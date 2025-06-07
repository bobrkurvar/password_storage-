from aiogram.fsm.state import StatesGroup, State


class InputPassword(StatesGroup):
    new_password = State()
    password = State()

class CreateAcc(StatesGroup):
    resource = State()
    password = State()