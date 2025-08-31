from aiogram import Router, F
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from utils import MyExternalApiForBot
from bot.utils.keyboards import get_inline_kb
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.filters.states import InputUser
from bot.filters import CallbackFactory
from bot.lexicon import phrases
from core.security import get_password_hash
import logging

router = Router()

log = logging.getLogger(__name__)

@router.callback_query(StateFilter(default_state), CallbackFactory.filter(F.act.lower() == 'sign up'))
async def press_button_sign_in(callback: CallbackQuery, ext_api_manager: MyExternalApiForBot, state: FSMContext):
    text = ("MENU")
    kb = get_inline_kb(text)
    user = await ext_api_manager.read(prefix='user', ident_val=callback.from_user.id)
    if not user:
        await callback.message.edit_text(text=phrases.register, reply_markup=kb)
        await state.set_state(InputUser.sign_up)
    else:
        await callback.message.edit_text(text=phrases.already_reg, reply_markup=kb)

@router.callback_query(StateFilter(default_state), CallbackFactory.filter(F.act.lower() == 'sign in'))
async def press_button_sign_up(callback: CallbackQuery, ext_api_manager: MyExternalApiForBot, state: FSMContext):
    text = ('MENU')
    kb = get_inline_kb(text)
    user = await ext_api_manager.read(prefix='user', ident_val=callback.from_user.id)
    if not user:
        await callback.message.edit_text(text=phrases.user_not_exists, reply_markup=kb)
    else:
        await callback.message.edit_text(text=phrases.login, reply_markup=kb)
        await state.set_state(InputUser.sign_in)

@router.message(StateFilter(InputUser.sign_in, InputUser.sign_up))
async def process_input_password_for_sign_in(message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot):
    msg = (await state.get_data()).get('msg')
    cur_state = await state.get_state()
    if cur_state == InputUser.sign_up:
        await ext_api_manager.create(prefix='user', id=message.from_user.id, password=get_password_hash(message.text),
                                     username=message.from_user.username)
        buttons = ('SIGN IN', 'SIGN UP')
    else:
        tokens = await ext_api_manager.login(id=message.from_user.id, password=message.text, username=message.from_user.username)
        access_token = tokens.get('access_token')
        access_time = 900
        #await state.update_data(access_token=access_token, ttl=access_time)
        await state.storage.set_token(state.key, token_name='access_token', token_value=access_token, ttl=access_time)
        refresh_token = tokens.get('refresh_token')
        refresh_time = 86400*7
        await state.storage.set_token(state.key, token_name='refresh_token', token_value=refresh_token, ttl=refresh_time)
        #await state.update_data(refresh_token=refresh_token, ttl=refresh_time)
        buttons = ('ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = (await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.start,
                                         reply_markup=kb)).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)
