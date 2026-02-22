import logging

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.dialog.states import InputUser
from bot.http_client import MyExternalApiForBot
from bot.services.auth import ensure_auth,match_status_and_interface
from bot.texts import phrases
from bot.utils.flow import get_state_from_status
from bot.utils.keyboards import get_inline_kb
from bot.services.exceptions import AuthError
from shared.adapters.redis import RedisService

router = Router()

log = logging.getLogger(__name__)


@router.message(StateFilter(InputUser.sign_in, InputUser.sign_up))
async def process_input_password(
    message: Message,
    state: FSMContext,
    ext_api_manager: MyExternalApiForBot,
    redis_service: RedisService,
):
    msg = (await state.get_data()).get("msg")
    cur_state = await state.get_state()
    previous_data = await redis_service.get(f"{message.from_user.id}:previous_data")
    previous_state, previous_text, previous_buttons = None, None, None
    if previous_data is not None:
        previous_state, previous_text, previous_buttons = (
            previous_data.get("state"),
            previous_data.get("text"),
            previous_data.get("buttons"),
        )
    new_state = None
    buttons = (
        ("ACCOUNTS", "CREATE ACCOUNT")
        if previous_buttons is None
        else previous_buttons
    )
    text = phrases.start if previous_text is None else previous_text
    if cur_state == InputUser.sign_up:
        log.debug("register - sign_up")
        await ext_api_manager.sign_up(
            message.from_user.id, message.from_user.username, message.text
        )
    else:
        try:
            token, status = await ensure_auth(
                ext_api_manager,
                redis_service,
                message.from_user.id,
                password=message.text,
            )
            text, buttons = match_status_and_interface(ok_text=text, ok_buttons=buttons)
            await ext_api_manager.master_key(access_token=token, password=message.text)
            await redis_service.pop(f"{message.from_user.id}:previous_data")
        except AuthError as exc:
            status = exc.status
            text, buttons = match_status_and_interface(status, text, buttons)
        new_state = get_state_from_status(status, previous_state)

    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    try:
        msg = (
            await message.bot.edit_message_text(
                chat_id=message.chat.id, message_id=msg, text=text, reply_markup=kb
            )
        ).message_id
    except TelegramBadRequest:
        pass
    await state.update_data(msg=msg)
    await state.set_state(new_state)
