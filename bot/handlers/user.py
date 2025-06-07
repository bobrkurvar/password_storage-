from aiogram import Router, F
from bot.filters import CallbackPasswordFactory
from aiogram.types import CallbackQuery, Message
from bot.utils import ExternalApi, get_inline_kb, get_hash_from_pas
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from bot.filters.states import InputPassword
from bot.lexicon import phrases
from core.security import get_password_hash
import logging

router = Router()

log = logging.getLogger('app.bot.handlers')

@router.callback_query(StateFilter(default_state), CallbackPasswordFactory.filter(F.act.lower().in_({'sign up', 'sing in'})))
async def process_sign_up(callback: CallbackQuery, state: FSMContext, callback_data: CallbackPasswordFactory):
    await callback.answer()
    kb = get_inline_kb('MENU')
    await callback.message.edit_text(text=phrases.password, reply_markup=kb)
    await state.set_state(InputPassword.new_password) if callback_data.act == 'sign up' else await state.set_state(InputPassword.password)

@router.message(StateFilter(InputPassword.new_password))
async def process_input_new_password(message: Message, state: FSMContext, ext_api_manager: ExternalApi):

    await message.delete()
    user_id  = await ext_api_manager.create(prefix='user', password=get_password_hash(message.text), username=message.from_user.username,
                                            id=message.from_user.id)
    log.info('создан пользователь: %s', user_id)
    msg = (await state.get_data()).get('msg')
    buttons = ('SIGN IN', 'SIGN UP', 'ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=user_id)
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.start,
                                         reply_markup=kb)
    await state.clear()
    await state.update_data(msg=msg.message_id)

@router.message(StateFilter(InputPassword.password))
async def process_input_password(message: Message, state: FSMContext, ext_api_manager: ExternalApi):
    await message.delete()
    user  = await ext_api_manager.login(prefix='user', password=get_password_hash(message.text), username=message.from_user.username,
                                            id=message.from_user.id)
    if not user.get('error'):
        log.info( 'пользователь %s не идентифицирован', message.from_user.username)
    else:
        log.info('пользователь %s идентифицирован', message.from_user.username)
    msg = (await state.get_data()).get('msg')
    buttons = ('SIGN IN', 'SIGN UP', 'ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons)
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.start,
                                         reply_markup=kb)
    await state.clear()
    await state.update_data(msg=msg.message_id)

