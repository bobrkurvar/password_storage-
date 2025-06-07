from aiogram import Router, F
from bot.filters import CallbackFactory
from bot.filters.states import InputAccount
from aiogram.types import CallbackQuery, Message
from bot.utils import ExternalApi, get_inline_kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from bot.lexicon import phrases

router = Router()

@router.callback_query(StateFilter(default_state), CallbackFactory.filter(F.act.lower()=='create account'))
async def process_create_account(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    kb = get_inline_kb('MENU')
    msg = await callback.message.edit_text(text=phrases.account_name, reply_markup=kb)
    await state.update_data(msg=msg.message_id)
    await state.set_state(InputAccount.name)

@router.message(StateFilter(InputAccount.name))
async def process_input_account_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.delete()
    msg = (await state.get_data()).get('msg')
    kb = get_inline_kb('MENU')
    msg = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.account_password,
                                        reply_markup=kb)
    await state.update_data(msg=msg.message_id)
    await state.set_state(InputAccount.password)

@router.message(StateFilter(InputAccount.password))
async def process_input_account_password(message: Message, state: FSMContext, ext_api_manager: ExternalApi):
    await message.delete()
    name=(await state.get_data()).get('name')
    msg = (await state.get_data()).get('msg')
    account = await ext_api_manager.create(prefix='account', name=name,
                                          password=message.text, user_id=message.from_user.id)
    kb = get_inline_kb('MENU')
    msg = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg,
                                        text=phrases.account_created.format(account), reply_markup=kb)
    await state.clear()
    await state.update_data(msg=msg.message_id)