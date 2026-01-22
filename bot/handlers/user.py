import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from bot.filters import CallbackFactory
from bot.filters.states import InputUser
from bot.lexicon import phrases
from services.bot.tokens import token_get_flow, TokenStatus
from bot.utils.keyboards import get_inline_kb
from shared import MyExternalApiForBot

token_status_to_state = {
    TokenStatus.SUCCESS: None,
    TokenStatus.NEED_PASSWORD: InputUser.sign_in,
    TokenStatus.NEED_REGISTRATION: InputUser.sign_up
}

router = Router()

log = logging.getLogger(__name__)


@router.callback_query(
    StateFilter(default_state), CallbackFactory.filter(F.act.lower() == "sign up")
)
async def press_button_sign_up(callback: CallbackQuery, state: FSMContext, ext_api_manager: MyExternalApiForBot):
    text = "MENU"
    kb = get_inline_kb(text)
    user = await ext_api_manager.read_user(user_id=callback.from_user.id)
    if not user:
        msg = (
            await callback.message.edit_text(text=phrases.register, reply_markup=kb)
        ).message_id
        await state.set_state(InputUser.sign_up)
    else:
        msg = (
            await callback.message.edit_text(text=phrases.already_reg, reply_markup=kb)
        ).message_id
    await state.update_data(msg=msg)


@router.callback_query(
    StateFilter(default_state), CallbackFactory.filter(F.act.lower() == "sign in")
)
async def press_button_sign_in(callback: CallbackQuery, state: FSMContext, ext_api_manager: MyExternalApiForBot):
    token, text, buttons, status = await token_get_flow(ext_api_manager, callback.from_user.id)
    if token:
        buttons += ("ACCOUNTS", "CREATE ACCOUNT")
    kb = get_inline_kb(*buttons)
    msg = (
        await callback.message.edit_text(
            text=text, reply_markup=kb
        )
    ).message_id
    new_state = token_status_to_state[status]
    await state.set_state(new_state)
    await state.update_data(msg=msg)


@router.message(StateFilter(InputUser.sign_in, InputUser.sign_up))
async def process_input_password(
    message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot
):
    msg = (await state.get_data()).get("msg")
    cur_state = await state.get_state()
    status = ""
    buttons = ("SIGN IN", "MENU")
    text = phrases.start
    if cur_state == InputUser.sign_up:
        await ext_api_manager.sign_up(message.from_user.id, message.from_user.username, message.text)
    else:
        token, text, buttons, status = await token_get_flow(ext_api_manager, message.from_user.id, message.text)
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = (
        await message.bot.edit_message_text(
            chat_id=message.chat.id, message_id=msg, text=text, reply_markup=kb
        )
    ).message_id
    new_state = token_status_to_state.get(status, None)
    await state.update_data(msg=msg)
    await state.set_state(new_state)
