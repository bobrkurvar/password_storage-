from aiogram.fsm.state import State

from bot.dialog.states import InputUser
from bot.services import AuthStage


def get_state_from_status(
    status: AuthStage | None = None, ok_state: State | str | None = None
):
    if status is None:
        return ok_state

    if isinstance(status, str):
        status = State(status)

    auth_status_to_state = {
        AuthStage.OK: ok_state,
        AuthStage.NEED_PASSWORD: InputUser.sign_in,
        AuthStage.NEED_REGISTRATION: InputUser.sign_up,
        AuthStage.WRONG_PASSWORD: InputUser.sign_in,
        AuthStage.NEED_UNLOCK: InputUser.sign_in,
    }

    return auth_status_to_state.get(status, None)


async def set_previous_data(
    redis_service, state, user_id, text: str | None = None, buttons=None
):
    previous_data = {"state": state.state}
    if text is not None:
        previous_data.update(text=text)
    if buttons is not None:
        previous_data.update(buttons=buttons)
    await redis_service.set(f"{user_id}:previous_data", previous_data)
