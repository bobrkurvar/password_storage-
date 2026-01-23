from services.bot.tokens import AuthStage
from bot.filters.states import InputUser
from aiogram.fsm.state import State


def get_state_from_status(status: AuthStage | None = None, ok_state: State | str | None = None):
    if status is None:
        return None

    if isinstance(status, str):
        status = State(status)

    auth_status_to_state = {
        AuthStage.OK: ok_state,
        AuthStage.NEED_PASSWORD: InputUser.sign_in,
        AuthStage.NEED_REGISTRATION: InputUser.sign_up,
        AuthStage.WRONG_PASSWORD: InputUser.sign_in,
        AuthStage.NEED_UNLOCK: InputUser.sign_in
    }

    return auth_status_to_state.get(status, None)
