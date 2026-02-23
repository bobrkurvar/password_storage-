from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.dialog.callback import CallbackFactory
from bot.services.exceptions import AuthError
from bot.services.messages import delete_msg_if_exists
from bot.texts import phrases
from bot.utils.keyboards import get_inline_kb
from bot.services.auth import ensure_auth, match_status_and_interface
from bot.http_client import MyExternalApiForBot
from shared.adapters.redis import RedisService
from bot.utils.flow import get_state_from_status

router = Router()


@router.message(CommandStart())
async def process_command_start(message: Message, ext_api_manager: MyExternalApiForBot, redis_service: RedisService, state: FSMContext):
    buttons = ("ACCOUNTS", "CREATE ACCOUNT", {"text": "DELETE ACCOUNT", "switch": "delete"})
    parts = message.text.split(maxsplit=1)
    new_state = None
    text = phrases.start
    if len(parts) > 1 and parts[1] == "auth":
        # Пользователь пришёл через кнопку "Нужна авторизация"
        try:
            _, status = await ensure_auth(ext_api_manager, redis_service, message.from_user.id)
            text, buttons = match_status_and_interface(ok_text=text)
        except AuthError as exc:
            status = exc.status
            text, buttons = match_status_and_interface(status)
        new_state = get_state_from_status(status)
    kb = get_inline_kb(*buttons)
    msg = (await state.get_data()).get("msg")
    await delete_msg_if_exists(msg, message, TelegramBadRequest)
    msg = (await message.answer(text=text, reply_markup=kb)).message_id
    await state.update_data(msg=msg)
    await state.set_state(new_state)


@router.callback_query(CallbackFactory.filter(F.act.lower() == "start"))
async def press_button_start(callback: CallbackQuery, state: FSMContext):
    buttons = ("ACCOUNTS", "CREATE ACCOUNT", {"text": "DELETE ACCOUNT", "switch": "delete"})
    kb = get_inline_kb(*buttons)
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
    kb = get_inline_kb("start")
    data = await state.get_data()
    msg = data.get("msg")
    await delete_msg_if_exists(msg, message, TelegramBadRequest)
    msg = (await message.answer(text=phrases.help, reply_markup=kb)).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)


@router.callback_query(CallbackFactory.filter(F.act.lower() == "menu"))
async def press_button_menu(callback: CallbackQuery, state: FSMContext):
    buttons = ("ACCOUNTS", "CREATE ACCOUNT", {"text": "DELETE ACCOUNT", "switch": "delete"})
    kb = get_inline_kb(*buttons)
    msg = (
        await callback.message.edit_text(text=phrases.start, reply_markup=kb)
    ).message_id
    await state.update_data(msg=msg)
    await state.set_state(None)
