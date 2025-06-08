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

@router.message(StateFilter(InputUser.password, InputUser.new_password))
async def process_input_password(message: Message, state: FSMContext, ext_api_manager: ExternalApi):
    await message.delete()
    cur_state = await state.get_state()
    if cur_state == InputUser.new_password:
        await ext_api_manager.create(prefix='user', id=message.from_user.id, password=get_password_hash(message.text),
                                     username=message.from_user.username)

    user_token = await ext_api_manager.login(prefix='user', password=message.text, username=message.from_user.username,
                                            id=message.from_user.id)
    if user_token:
        user_token=user_token.get('access_token')
    msg = (await state.get_data()).get('msg')
    buttons = ('ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.start,
                                         reply_markup=kb)
    await state.clear()
    await state.update_data(msg=msg.message_id)
    if user_token:
        await state.update_data(token=user_token)

