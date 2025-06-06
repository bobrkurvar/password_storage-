from aiogram import Router, F
from bot.filters import CallbackPasswordFactory
from aiogram.types import CallbackQuery, Message
from bot.utils import ExternalApi, get_inline_kb, get_hash_from_pas
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from bot.filters.states import UserStates
from bot.lexicon import phrases
import logging

router = Router()

log = logging.getLogger('app.bot.handlers.user')

@router.callback_query(StateFilter(default_state), CallbackPasswordFactory.filter(F.act.lower()=='auth'))
async def process_register(callback: CallbackQuery, callback_data: CallbackPasswordFactory, state: FSMContext):
    await callback.answer()
    kb = get_inline_kb('MENU')
    msg = await callback.message.edit_text(text=phrases.login, reply_markup=kb)
    await state.update_data(msg=msg.message_id)
    await state.set_state(UserStates.login)

@router.message(StateFilter(UserStates.login))
async def process_input_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.delete()
    kb = get_inline_kb('MENU')
    msg = (await state.get_data()).get('msg')
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg,
                                        text=phrases.password, reply_markup=kb)
    await state.set_state(UserStates.password)

@router.message(StateFilter(UserStates.password))
async def process_input_password(message: Message, state: FSMContext, ext_api_manager: ExternalApi):
    is_user_ident: bool = await ext_api_manager.auth(prefix='user', ident='id', ident_val=message.from_user.id,
                                      password=message.text)
    await message.delete()
    msg = (await state.get_data()).get('msg')
    # await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.start,
    #                                     reply_markup=kb)