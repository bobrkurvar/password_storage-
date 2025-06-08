from aiogram import Router, F
from bot.filters import CallbackFactory
from aiogram.types import CallbackQuery, Message
from bot.utils import ExternalApi, get_inline_kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from bot.filters.states import InputUser
from bot.lexicon import phrases
from core.security import get_password_hash
import logging

router = Router()

log = logging.getLogger('app.bot.handlers.user')

@router.callback_query(StateFilter(default_state), CallbackFactory.filter(F.act.lower().in_({'sign up', 'sign in'})))
async def process_sign_up(callback: CallbackQuery, state: FSMContext, callback_data: CallbackFactory):
    await callback.answer()
    kb = get_inline_kb('MENU')
    msg = await callback.message.edit_text(text=phrases.password, reply_markup=kb)
    await state.update_data(msg=msg.message_id)
    if callback_data.act.lower() == 'sign up':
        await state.set_state(InputUser.new_password)
    else:
        await state.set_state(InputUser.password)

@router.message(StateFilter(InputUser.new_password))
async def process_input_new_password(message: Message, state: FSMContext, ext_api_manager: ExternalApi):

    await message.delete()
    user_id  = await ext_api_manager.create(prefix='user', password=get_password_hash(message.text), username=message.from_user.username,
                                            id=message.from_user.id)
    log.info('создан пользователь: %s', user_id)
    msg = (await state.get_data()).get('msg')
    buttons = ('SIGN IN', 'SIGN UP', 'ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=user_id)
    msg = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.start,
                                         reply_markup=kb)
    await state.clear()
    await state.update_data(msg=msg.message_id)

@router.message(StateFilter(InputUser.password))
async def process_input_password(message: Message, state: FSMContext, ext_api_manager: ExternalApi):
    await message.delete()
    user_token  = await ext_api_manager.login(prefix='user', password=message.text, username=message.from_user.username,
                                            id=message.from_user.id)
    if user_token:
        user_token=user_token.get('access_token')
    print(50*'-', user_token, 50*'-', sep='\n')
    msg = (await state.get_data()).get('msg')
    buttons = ('SIGN IN', 'SIGN UP', 'ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.start,
                                         reply_markup=kb)
    await state.clear()
    await state.update_data(msg=msg.message_id, token=user_token)

