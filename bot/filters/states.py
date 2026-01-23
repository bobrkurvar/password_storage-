from aiogram.fsm.state import State, StatesGroup


class InputUser(StatesGroup):
    sign_in = State()
    sign_up = State()

class InputAccount(StatesGroup):
    name = State()
    password = State()
    params = State()
    input = State()

class DeleteAccount(StatesGroup):
    choice = State()
