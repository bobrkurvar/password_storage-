from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.filters.callback_factory import CallbackFactory
from bot.lexicon import phrases
from bot.utils.keyboards import get_inline_kb
from services.bot.messages import delete_msg_if_exists

router = Router()


@router.message(CommandStart())
async def process_command_start(message: Message, state: FSMContext):
    buttons = ("ACCOUNTS", "CREATE ACCOUNT", "DELETE ACCOUNT")
    kb = get_inline_kb(*buttons, user_id=message.from_user.id)
    msg = (await state.get_data()).get("msg")
    await delete_msg_if_exists(msg, message, TelegramBadRequest)
    msg = (await message.answer(text=phrases.start, reply_markup=kb)).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)


@router.callback_query(CallbackFactory.filter(F.act.lower() == "start"))
async def press_button_start(callback: CallbackQuery, state: FSMContext):
    buttons = ("ACCOUNTS", "CREATE ACCOUNT", "DELETE ACCOUNT")
    kb = get_inline_kb(*buttons, user_id=callback.from_user.id)
    msg = (
        await callback.message.edit_text(text=phrases.start, reply_markup=kb)
    ).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)


@router.message(
    Command(
        commands=[
            "help",
        ]
    )
)
async def process_command_help(message: Message, state: FSMContext):
    kb = get_inline_kb("start", user_id=message.from_user.id)
    data = await state.get_data()
    msg = data.get("msg")
    await delete_msg_if_exists(msg, message, TelegramBadRequest)
    msg = (await message.answer(text=phrases.help, reply_markup=kb)).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)


@router.callback_query(CallbackFactory.filter(F.act.lower() == "menu"))
async def press_button_menu(callback: CallbackQuery, state: FSMContext):
    buttons = ("ACCOUNTS", "CREATE ACCOUNT", "DELETE ACCOUNT")
    kb = get_inline_kb(*buttons, user_id=callback.from_user.id)
    msg = (
        await callback.message.edit_text(text=phrases.start, reply_markup=kb)
    ).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)
