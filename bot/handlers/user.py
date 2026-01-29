import logging

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from shared.adapters.external import MyExternalApiForBot

from bot.dialog.states import InputUser
from bot.texts import phrases
from bot.services.tokens import match_status_and_interface, AuthStage
from bot.utils.flow import get_state_from_status
from bot.utils.keyboards import get_inline_kb
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
        ("ACCOUNTS", "CREATE ACCOUNT", "DELETE ACCOUNT")
        if previous_buttons is None
        else previous_buttons
    )
    text = phrases.start if previous_text is None else previous_text
    if cur_state == InputUser.sign_up:
        await ext_api_manager.sign_up(
            message.from_user.id, message.from_user.username, message.text
        )
    else:
        status, _, _, text, buttons = await match_status_and_interface(
            ext_api_manager,
            redis_service,
            message.from_user.id,
            text,
            buttons,
            password=message.text,
            need_crypto=True,
        )
        if status == AuthStage.OK:
            await redis_service.pop(f"{message.from_user.id}:previous_data")
        new_state = get_state_from_status(status, previous_state)

    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = (
        await message.bot.edit_message_text(
            chat_id=message.chat.id, message_id=msg, text=text, reply_markup=kb
        )
    ).message_id
    await state.update_data(msg=msg)
    await state.set_state(new_state)
