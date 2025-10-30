import base64
import logging
import os

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from bot.filters import CallbackFactory
from bot.filters.states import InputUser
from bot.lexicon import phrases
from bot.utils.keyboards import get_inline_kb
from core.security import get_password_hash
from shared import MyExternalApiForBot

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
async def press_button_sign_up(callback: CallbackQuery, state: FSMContext):
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
    if cur_state == InputUser.sign_up:
        salt = base64.b64encode(os.urandom(16)).decode("utf-8")
        await ext_api_manager.create(
            prefix="user",
            id=message.from_user.id,
            password=get_password_hash(message.text),
            username=message.from_user.username,
            salt=salt,
        )
        admins = (await state.get_data()).get("admins")
        role_name = "admin" if message.from_user.id in admins else "user"
        role = (await ext_api_manager.read(prefix="user/roles", role_name=role_name))[0]
        role_id = role.get("role_id")
        log.debug("role_id: %s", role_id)
        await ext_api_manager.create(
            prefix=f"user/{message.from_user.id}/roles",
            role_name="user",
            role_id=role_id,
        )
        buttons = ("SIGN IN", "MENU")
    else:
        tokens = await ext_api_manager.login(
            client_id=message.from_user.id,
            password=message.text,
            username=message.from_user.username,
        )
        log.debug("tokens %s", tokens)
        if None in tokens.values():
            log.debug("НЕПРАВЛЬНЫЙ ПАРОЛЬ")
            buttons = ("SIGN IN", "MENU")
            kb = get_inline_kb(*buttons, user_id=message.from_user.id)
            msg = (
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=msg,
                    text="Неправильный пароль",
                    reply_markup=kb,
                )
            ).message_id
            await state.update_data(msg=msg)
            await state.set_state(None)
            return
        await state.update_data(master_password=message.text)
        access_token = tokens.get("access_token")
        access_time = 900
        await state.storage.set_token(
            state.key,
            token_name="access_token",
            token_value=access_token,
            ttl=access_time,
        )
        refresh_token = tokens.get("refresh_token")
        refresh_time = 86400 * 7
        await state.storage.set_token(
            state.key,
            token_name="refresh_token",
            token_value=refresh_token,
            ttl=refresh_time,
        )
        buttons = ("ACCOUNTS", "CREATE ACCOUNT")
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = (
        await message.bot.edit_message_text(
            chat_id=message.chat.id, message_id=msg, text=phrases.start, reply_markup=kb
        )
    ).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)
