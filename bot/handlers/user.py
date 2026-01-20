import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from bot.filters import CallbackFactory
from bot.filters.states import InputUser
from bot.lexicon import phrases
from bot.utils.keyboards import get_inline_kb
from shared import MyExternalApiForBot
from services.bot.users import user_sign_up, user_sign_in

router = Router()

log = logging.getLogger(__name__)


@router.callback_query(
    StateFilter(default_state), CallbackFactory.filter(F.act.lower() == "sign up")
)
async def press_button_sign_up(callback: CallbackQuery, state: FSMContext):
    text = "MENU"
    kb = get_inline_kb(text)
    data = await state.get_data()
    user = data.get("user_info")
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
async def press_button_sign_in(callback: CallbackQuery, state: FSMContext):
    text = "MENU"
    kb = get_inline_kb(text)
    data = await state.get_data()
    user = data.get("user_salt")
    if not user:
        msg = (
            await callback.message.edit_text(
                text=phrases.user_not_exists, reply_markup=kb
            )
        ).message_id
    else:
        msg = (
            await callback.message.edit_text(text=phrases.login, reply_markup=kb)
        ).message_id
        await state.set_state(InputUser.sign_in)
    await state.update_data(msg=msg)


@router.message(StateFilter(InputUser.sign_in, InputUser.sign_up))
async def process_input_password_for_sign_in(
    message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot
):
    msg = (await state.get_data()).get("msg")
    cur_state = await state.get_state()
    buttons = ("SIGN IN", "MENU")
    text = phrases.start
    if cur_state == InputUser.sign_up:
        await user_sign_up(state, message, ext_api_manager)
    elif not await user_sign_in(state, message, ext_api_manager):
        text = "Неправильный пароль"
    else:
        buttons = ("ACCOUNTS", "CREATE ACCOUNT")
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = (
        await message.bot.edit_message_text(
            chat_id=message.chat.id, message_id=msg, text=text, reply_markup=kb
        )
    ).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)
