from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from bot.utils import get_inline_kb
from bot.lexicon import phrases
from bot.filters.callback_factory import CallbackFactory
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(CommandStart())
async def process_command_start(message: Message, state: FSMContext):
    await message.delete()
    buttons = ('ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    data = await state.get_data()
    msg = data.get('msg')
    if not msg:
        msg = await message.answer(text=phrases.start, reply_markup=kb)
    else:
        if message.text != phrases.start:
            msg = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.start,
                                            reply_markup=kb)
    await state.clear()
    data.update(msg=msg.message_id)
    await state.update_data(data)

@router.message(Command(commands=['help', ]))
async def process_command_help(message: Message, state: FSMContext):
    await message.delete()
    kb = get_inline_kb('start', user_id=message.from_user.id)
    data = await state.get_data()
    msg = data.get('msg')
    if not msg:
        msg = await message.answer(text=phrases.help, reply_markup=kb)
    else:
        if message.text != phrases.help:
            msg = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.help,
                                            reply_markup=kb)
    await state.clear()
    data.update(msg=msg.message_id)
    await state.update_data(data)


@router.callback_query(CallbackFactory.filter(F.act.lower() == 'start'))
async def process_button_start(callback: CallbackQuery, state: FSMContext):
    #await callback.answer()
    buttons = ('ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=callback.from_user.id)
    msg = await callback.message.edit_text(text=phrases.start, reply_markup=kb)
    await state.update_data(msg=msg.message_id)

@router.callback_query(CallbackFactory.filter(F.act.lower() == 'menu'))
async def process_button_menu(callback: CallbackQuery, state: FSMContext):
    #await callback.answer()
    data = await state.get_data()
    buttons = ('ACCOUNTS', 'CREATE ACCOUNT')
    kb = get_inline_kb(*buttons, user_id=callback.from_user.id)
    msg = await callback.message.edit_text(text=phrases.start, reply_markup=kb)
    data.update(msg=msg.message_id)
    await state.clear()
    await state.update_data(data)