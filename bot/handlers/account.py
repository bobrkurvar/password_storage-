import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from bot.dialog.callback import CallbackFactory
from bot.dialog.states import InputAccount
from bot.http_client import MyExternalApiForBot
from bot.services.auth import (action_with_unlock_storage, ensure_auth,
                               match_status_and_interface)
from bot.services.exceptions import AuthError
from bot.services.messages import delete_msg_if_exists
from bot.texts import phrases
from bot.utils.flow import get_state_from_status, set_previous_data
from bot.utils.keyboards import get_inline_kb
from shared.adapters.redis import RedisService

router = Router()
log = logging.getLogger(__name__)


@router.callback_query(
    StateFilter(default_state),
    CallbackFactory.filter(F.act.lower() == "create account"),
)
async def process_create_account(
    callback: CallbackQuery,
    state: FSMContext,
    ext_api_manager: MyExternalApiForBot,
    redis_service: RedisService,
):
    try:
        _, status = await ensure_auth(
            ext_api_manager, redis_service, callback.from_user.id
        )
        text, buttons = match_status_and_interface(ok_text=phrases.account_name)
    except AuthError as exc:
        status = exc.status
        text, buttons = match_status_and_interface(status)
        await set_previous_data(
            redis_service,
            InputAccount.name,
            callback.from_user.id,
            phrases.account_name,
            ("MENU",),
        )
    new_state = get_state_from_status(status, InputAccount.name)
    kb = get_inline_kb(*buttons)
    msg = (await callback.message.edit_text(text=text, reply_markup=kb)).message_id
    await state.update_data(msg=msg)
    await state.set_state(new_state)


@router.message(StateFilter(InputAccount.name))
async def process_input_account_name(message: Message, state: FSMContext):
    kb = get_inline_kb("MENU")
    msg = (await state.get_data()).get("msg")
    await delete_msg_if_exists(msg, message, TelegramBadRequest)
    msg = (
        await message.answer(text=phrases.account_password, reply_markup=kb)
    ).message_id
    await state.update_data(name=message.text, msg=msg)
    await state.set_state(InputAccount.password)


@router.message(StateFilter(InputAccount.password))
async def process_input_account_password(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    data.update(account_password=message.text)
    buttons = ("MENU",)
    kb = get_inline_kb(*buttons)
    msg = data.get("msg")
    await delete_msg_if_exists(msg, message, TelegramBadRequest)
    msg = (
        await message.answer(text=phrases.account_params, reply_markup=kb)
    ).message_id
    data.update(msg=msg)
    await state.update_data(data)
    await state.set_state(InputAccount.params)


@router.message(StateFilter(InputAccount.params))
async def process_params_list(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    msg = data.get("msg")
    params = [
        p.strip()
        for p in message.text.split()
        if p.strip() and p not in {"password", "name"}
    ]

    if not params:
        await delete_msg_if_exists(msg, message, TelegramBadRequest)
        await message.answer("Нет параметров")
        return

    await state.update_data(
        {
            "params": params,
            "index": 0,
            "collected": [],
        }
    )

    await delete_msg_if_exists(msg, message, TelegramBadRequest)
    kb = get_inline_kb("MENU", "SECRET")
    msg = (await message.answer(f"Введите {params[0]}", reply_markup=kb)).message_id
    await state.update_data(msg=msg)
    await state.set_state(InputAccount.input)


@router.message(StateFilter(InputAccount.input))
async def process_select_account_params(
    message: Message,
    state: FSMContext,
    ext_api_manager: MyExternalApiForBot,
    redis_service: RedisService,
):
    data, cur_state = await state.get_data(), await state.get_state()
    msg, params, i = data["msg"], data["params"], data["index"]
    buttons = ("MENU",)
    text = phrases.start
    status, proceed = None, True

    if params:
        current_param = params[i]
        content = message.text
        secret = data.pop("secret", False)
        text = f"Введите {current_param}"
        buttons = ("MENU", "SECRET")
        data["collected"].append(
            {
                "name": current_param,
                "content": content,
                "secret": secret,
            }
        )
        i += 1
        data["index"] = i

    if i == len(params):
        data.pop("params")
        data.pop("index")
        account_password, account_name = data.pop("account_password"), data.pop("name")
        try:
            token, status = await ensure_auth(
                ext_api_manager,
                redis_service,
                message.from_user.id,
            )
            await action_with_unlock_storage(
                lambda: ext_api_manager.create_account(password=account_password, access_token=token, account_name=account_name, params=data["collected"]),
            )
            text, buttons = match_status_and_interface(
                ok_text=phrases.account_created.format(account_name)
            )
            data.pop("collected")
        except AuthError as exc:
            status = exc.status
            text, buttons = match_status_and_interface(status)
            await set_previous_data(
                redis_service,
                cur_state,
                message.from_user.id,
                phrases.account_created.format(account_name),
                ("MENU",),
            )

    new_state = get_state_from_status(status, cur_state)
    await delete_msg_if_exists(msg, message)
    kb = get_inline_kb(*buttons)
    msg = (await message.answer(text=text, reply_markup=kb)).message_id
    data.update(msg=msg)
    await state.set_data(data)
    await state.set_state(new_state)


@router.callback_query(
    StateFilter(InputAccount.params, InputAccount.input),
    CallbackFactory.filter(F.act.lower() == "secret"),
)
async def press_button_secret_param(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cur_par = data["params"][data["index"]]
    kb = get_inline_kb("MENU")
    msg = (
        await callback.message.edit_text(text=f"Введите {cur_par}", reply_markup=kb)
    ).message_id
    await state.update_data(msg=msg, secret=True)


@router.callback_query(
    StateFilter(default_state), CallbackFactory.filter(F.act.lower() == "accounts")
)
async def press_button_accounts(
    callback: CallbackQuery, ext_api_manager: MyExternalApiForBot, redis_service: RedisService, state: FSMContext
):
    try:
        token, status = await ensure_auth(ext_api_manager, redis_service, callback.from_user.id)
        accounts = await action_with_unlock_storage(lambda: ext_api_manager.read_own_account(access_token=token))
        log.debug("accounts: %s", accounts)
        ok_text = ""
        for account in accounts:
            for k, v in account.items():
                ok_text += phrases.account_param.format(k, v)
        ok_text = ok_text if ok_text != "" else phrases.empty_accounts_list
        text, buttons = match_status_and_interface(ok_text=ok_text)
    except AuthError as exc:
        status = exc.status
        text, buttons = match_status_and_interface(status)
    kb = get_inline_kb(*buttons)
    new_state = get_state_from_status(status)
    msg = (await callback.message.edit_text(text=text, reply_markup=kb)).message_id
    await state.set_state(new_state)
    await state.update_data(msg=msg)
