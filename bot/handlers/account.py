import base64
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from bot.filters import CallbackFactory
from bot.filters.states import InputAccount
from bot.lexicon import phrases
from bot.utils.keyboards import get_inline_kb
from core.security import decrypt_account_content, encrypt_account_content
from services.shared.external import MyExternalApiForBot
from services.shared.redis import RedisService
from services.bot.tokens import AuthStage, match_status_and_interface
from services.bot.messages import delete_msg_if_exists, set_previous_data
from bot.utils.flow import get_state_from_status
from bot.filters.states import InputUser


router = Router()
log = logging.getLogger(__name__)


@router.callback_query(
    StateFilter(default_state),
    CallbackFactory.filter(F.act.lower() == "create account"),
)
async def process_create_account(callback: CallbackQuery, state: FSMContext, ext_api_manager: MyExternalApiForBot, redis_service: RedisService):
    status, token, _, text, buttons = await match_status_and_interface(ext_api_manager, redis_service, callback.from_user.id, phrases.account_name)
    new_state = get_state_from_status(status, InputAccount.name)
    kb = get_inline_kb(*buttons)
    msg = (
        await callback.message.edit_text(text=text, reply_markup=kb)
    ).message_id
    await state.set_state(new_state)
    await state.update_data(msg=msg)


@router.message(StateFilter(InputAccount.name))
async def process_input_account_name(message: Message, state: FSMContext):
    kb = get_inline_kb("MENU")
    msg = (await state.get_data()).get("msg")
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
    except TelegramBadRequest:
        pass
    msg = (
        await message.answer(text=phrases.account_password, reply_markup=kb)
    ).message_id
    await state.update_data(name=message.text, msg=msg)
    await state.set_state(InputAccount.password)


@router.message(StateFilter(InputAccount.password))
async def process_input_account_password(
    message: Message, ext_api_manager: MyExternalApiForBot, state: FSMContext, redis_service: RedisService
):
    status, token, derive_key, text, buttons = await match_status_and_interface(ext_api_manager, redis_service, message.from_user.id, phrases.account_params, need_crypto=True)
    data = await state.get_data()
    new_state = get_state_from_status(status, InputAccount.params)
    if status == AuthStage.OK:
        data.update(account_password=message.text)
    kb = get_inline_kb(*buttons)
    msg = data.get("msg")
    await delete_msg_if_exists(msg, message, TelegramBadRequest)
    msg = (await message.answer(text=text, reply_markup=kb)).message_id
    data.update(msg=msg)
    await state.update_data(data)
    await state.set_state(new_state)


@router.message(StateFilter(InputAccount.params))
async def process_params_list(
    message: Message,
    state: FSMContext,
):
    params = [
        p.strip()
        for p in message.text.split()
        if p.strip() and p not in {"password", "name"}
    ]

    if not params:
        await message.answer("Нет параметров")
        return

    await state.update_data({
        "params": params,
        "index": 0,
        "collected": [],
    })

    kb = get_inline_kb("MENU", "SECRET")
    await message.answer(f"Введите {params[0]}", reply_markup=kb)
    await state.set_state(InputAccount.input)

@router.message(StateFilter(InputAccount.input))
async def process_select_account_params(
    message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot, redis_service: RedisService
):
    data = await state.get_data()
    cur_state = await state.get_state()
    account_name = data["name"]
    account_password = data["account_password"]
    msg = data.get("msg")
    params = data["params"]
    i = data["index"]
    buttons = ("MENU",)
    text = phrases.start
    status = None
    proceed = True

    if params:
        current_param = params[i]
        content = message.text
        secret = data.pop("secret", False)
        text = f"Введите {current_param}"
        buttons = ("MENU", "SECRET")

        if secret:
            status, token, derive_key, text, buttons = await match_status_and_interface(ext_api_manager, redis_service, message.from_user.id, ok_text=text, ok_buttons=buttons, need_crypto=True)
            if status == AuthStage.OK:
                content = encrypt_account_content(content, derive_key)
            else:
                proceed = False
                #await set_previous_data(redis_service, user_id=message.from_user.id, state=cur_state, text=text, buttons=buttons)

        if proceed:
            data["collected"].append({
                "name": current_param,
                "content": content,
                "secret": secret,
            })
            i += 1
            data["index"] = i

    if i == len(params):
        data.pop("params")
        data.pop("index")
        #await set_previous_data(redis_service, user_id=message.from_user.id, state=cur_state, text=text, buttons=buttons)
        status, token, derive_key, text, buttons = await match_status_and_interface(ext_api_manager, redis_service, message.from_user.id, ok_text=phrases.account_created.format(account_name), need_crypto=True)
        if token:
            await ext_api_manager.create_account(
                access_token=token,
                password = account_password,
                account_name = account_name,
                params = data["collected"]
            )
        data.pop("collected")
    await delete_msg_if_exists(msg, message)
    kb = get_inline_kb(**buttons)
    msg = (await message.answer(text=text, reply_markup=kb)).message_id
    data.update(msg=msg)
    new_state = get_state_from_status(status)
    await state.set_data(data)
    await state.set_state(new_state)


@router.callback_query(
    StateFilter(InputAccount.params, InputAccount.input),
    CallbackFactory.filter(F.act.lower() == "secret"),
)
async def press_button_secret_param(callback: CallbackQuery, state: FSMContext):
    cur_par = (await state.get_data()).get("params_lst")[0]
    kb = get_inline_kb("MENU")
    msg = (
        await callback.message.edit_text(text=f"Введите {cur_par}", reply_markup=kb)
    ).message_id
    await state.update_data(msg=msg, secret=True)


# @router.callback_query(
#     StateFilter(default_state), CallbackFactory.filter(F.act.lower() == "accounts")
# )
# async def press_button_accounts(
#     callback: CallbackQuery, ext_api_manager: MyExternalApiForBot, state: FSMContext
# ):
#     data = await state.get_data()
#     token, derive_key, text, buttons, status = await token_get_flow(ext_api_manager, callback.from_user.id)
#     log.debug("derive_key: %s", derive_key)
#     if token:
#         accounts = await ext_api_manager.read_account(
#             access_token=token,
#             user_id=callback.from_user.id,
#         )
#         account_params = []
#         for account in accounts:
#             item = {"account name": account["name"]}
#             params = await ext_api_manager.read_params(
#                 access_token=token,
#                 account_id=account["id"]
#             )
#             for param in params:
#                 content = param["content"]
#                 if param.get("secret") or param.get("name") == "password":
#                     encrypted_bytes = base64.urlsafe_b64decode(content)
#                     content = decrypt_account_content(encrypted_bytes, derive_key)
#                 item.update({"parameter": param["name"], "content": content})
#             account_params.append(item)
#
#         if account_params:
#             text = "<b>Список аккаунтов:\n</b>"
#             for param in account_params:
#                 text += f'{param["name"]}: {param["content"]}'
#         else:
#             text = "<b>\t\t\tСписок аккаунтов пуст</b>"
#     kb = get_inline_kb(*buttons)
#     msg = (await callback.message.edit_text(text=text, reply_markup=kb)).message_id
#     data.update(msg=msg)
#     new_state = token_status_to_state.get(status, None)
#     await state.set_state(new_state)
#     await state.update_data(data)
#
#
# @router.callback_query(
#     StateFilter(default_state),
#     CallbackFactory.filter(F.act.lower() == "delete account"),
# )
# async def press_button_delete_account(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     to_delete_lst = data.get("acc_params_lst")
#     if not to_delete_lst:
#         kb = get_inline_kb("MENU")
#         msg = (
#             await callback.message.edit_text(text="empty account_lst", reply_markup=kb)
#         ).message_id
#     else:
#         log.debug("to_delete_lst: %s", to_delete_lst)
#         buttons_data_lst = []
#         [
#             buttons_data_lst.append({"account_id": i.get("acc_id")})
#             for i in to_delete_lst
#             if {"account_id": i.get("acc")} not in buttons_data_lst
#         ]
#         log.debug("buttons_data_lst: %s", buttons_data_lst)
#         view_lst = []
#         [
#             view_lst.append(str(i.get("acc_id")))
#             for i in to_delete_lst
#             if str(i.get("acc_id")) not in view_lst
#         ]
#         kb = get_inline_kb(
#             *view_lst, "ALL", "MENU", width=3, buttons_data_lst=buttons_data_lst
#         )
#         msg = (
#             await callback.message.edit_text(text="choice account", reply_markup=kb)
#         ).message_id
#         await state.set_state(DeleteAccount.choice)
#     await state.update_data(msg=msg)
#
#
# @router.callback_query(StateFilter(DeleteAccount.choice), CallbackFactory.filter())
# async def process_delete_account(
#     callback: CallbackQuery,
#     ext_api_manager: MyExternalApiForBot,
#     state: FSMContext,
#     callback_data: CallbackFactory,
# ):
#     kb = get_inline_kb("MENU")
#     data = await state.get_data()
#     access_token = await state.storage.get_token(state.key, "access_token")
#     log.debug("token: %s", access_token)
#     if callback_data.act.lower() == "all":
#         await ext_api_manager.remove(
#             "account",
#             ident="user_id",
#             ident_val=callback.from_user.id,
#             access_token=access_token,
#         )
#         data.pop("acc_params_lst")
#     else:
#         await ext_api_manager.remove(
#             "account", ident=callback_data.account_id, access_token=access_token
#         )
#         acc_params_lst = data.get("acc_params_lst")
#         acc_params_lst = [
#             item
#             for item in acc_params_lst
#             if item.get("acc_id") != callback_data.account_id
#         ]
#         data.update(acc_params_lst=acc_params_lst)
#     msg = (
#         await callback.message.edit_text(text="account deleted", reply_markup=kb)
#     ).message_id
#     data.update(msg=msg)
#     await state.set_data(data)
#     await state.set_state(None)
