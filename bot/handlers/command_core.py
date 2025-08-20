from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from bot.utils.keyboards import get_inline_kb
from utils import MyExternalApiForBot
from bot.lexicon import phrases
from bot.filters.callback_factory import CallbackFactory
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(CommandStart())
async def process_command_start(message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot):
    buttons = ('ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    data = await state.get_data()
    msg = data.get('msg')
    if msg:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
        except TelegramBadRequest:
            pass
    msg = (await message.answer(text=phrases.start, reply_markup=kb)).message_id
    data.update(msg=msg)
    await ext_api_manager.login(prefix='/login')
    await state.clear()
    await state.update_data(data)

@router.message(Command(commands=['help', ]))
async def process_command_help(message: Message, state: FSMContext):
    kb = get_inline_kb('start', user_id=message.from_user.id)
    data = await state.get_data()
    msg = data.get('msg')
    if msg:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
        except TelegramBadRequest:
            pass
    msg = (await message.answer(text=phrases.help, reply_markup=kb)).message_id
    data.update(msg=msg)
    await state.clear()
    await state.update_data(data)

@router.callback_query(CallbackFactory.filter(F.act.lower() == 'start'))
async def process_button_start(callback: CallbackQuery, state: FSMContext, ext_api_manager: MyExternalApiForBot):
    buttons = ('ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=callback.from_user.id)
    msg = (await callback.message.edit_text(text=phrases.start, reply_markup=kb)).message_id
    await ext_api_manager.login(prefix='/login')
    await state.update_data(msg=msg)

@router.callback_query(CallbackFactory.filter(F.act.lower() == 'menu'))
async def process_button_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    buttons = ('ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=callback.from_user.id)
    msg = (await callback.message.edit_text(text=phrases.start, reply_markup=kb)).message_id
    data.update(msg=msg)
    await state.clear()
    await state.update_data(data)