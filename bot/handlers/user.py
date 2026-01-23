import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from bot.filters import CallbackFactory
from bot.filters.states import InputUser
from bot.lexicon import phrases
from services.bot.tokens import match_status_and_interface
from bot.utils.flow import get_state_from_status
from bot.utils.keyboards import get_inline_kb
from services.shared import MyExternalApiForBot
from services.shared.redis import RedisService


router = Router()

log = logging.getLogger(__name__)


# @router.callback_query(
#     StateFilter(default_state), CallbackFactory.filter(F.act.lower() == "sign up")
# )
# async def press_button_sign_up(callback: CallbackQuery, state: FSMContext, ext_api_manager: MyExternalApiForBot):
#     kb = get_inline_kb("MENU")
#     user = await ext_api_manager.read_user(user_id=callback.from_user.id)
#     if not user:
#         text = phrases.register
#         await state.set_state(InputUser.sign_up)
#     else:
#         text = phrases.already_reg
#     msg = (
#         await callback.message.edit_text(text=text, reply_markup=kb)
#     ).message_id
#     await state.update_data(msg=msg)
#
#
# @router.callback_query(
#     StateFilter(default_state), CallbackFactory.filter(F.act.lower() == "sign in")
# )
# async def press_button_sign_in(callback: CallbackQuery, state: FSMContext, ext_api_manager: MyExternalApiForBot, redis_service: RedisService):
#     default_text = phrases.start
#     default_buttons = ("ACCOUNTS", "CREATE ACCOUNT", "MENU")
#     status, token, _, text, buttons = await match_status_and_interface(ext_api_manager, redis_service, callback.from_user.id, default_text, default_buttons)
#     kb = get_inline_kb(*buttons)
#     msg = (
#         await callback.message.edit_text(
#             text=text, reply_markup=kb
#         )
#     ).message_id
#     new_state = get_state_from_status(status, InputUser.sign_in)
#     await state.set_state(new_state)
#     await state.update_data(msg=msg)


@router.message(StateFilter(InputUser.sign_in, InputUser.sign_up))
async def process_input_password(
    message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot, redis_service: RedisService
):
    msg = (await state.get_data()).get("msg")
    cur_state = await state.get_state()
    previous_state = await redis_service.get(f"{message.from_user.id}:previous_state")
    new_state = None
    buttons = ("SIGN IN", "MENU")
    text = phrases.start
    if cur_state == InputUser.sign_up:
        await ext_api_manager.sign_up(message.from_user.id, message.from_user.username, message.text)
    else:
        status, token, _, text, buttons = await match_status_and_interface(ext_api_manager, redis_service, message.from_user.id, text, password=message.text)
        new_state = get_state_from_status(status, previous_state)
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = (
        await message.bot.edit_message_text(
            chat_id=message.chat.id, message_id=msg, text=text, reply_markup=kb
        )
    ).message_id
    await state.update_data(msg=msg)
    await state.set_state(new_state)
