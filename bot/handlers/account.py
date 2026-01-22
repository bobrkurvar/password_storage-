import base64
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from bot.filters import CallbackFactory
from bot.filters.states import DeleteAccount, InputAccount
from bot.lexicon import phrases
from bot.utils.keyboards import get_inline_kb
from core.security import decrypt_account_content, encrypt_account_content
from shared.external import MyExternalApiForBot
from services.bot.accounts import make_secret
from services.bot.tokens import token_get_flow, TokenStatus
from services.bot.messages import delete_msg_if_exists
from bot.filters.states import InputUser

token_status_to_state = {
    TokenStatus.NEED_PASSWORD: InputUser.sign_in,
    TokenStatus.NEED_REGISTRATION: InputUser.sign_up
}

router = Router()
log = logging.getLogger(__name__)


@router.callback_query(
    StateFilter(default_state),
    CallbackFactory.filter(F.act.lower() == "create account"),
)
async def process_create_account(callback: CallbackQuery, state: FSMContext, ext_api_manager: MyExternalApiForBot):
    token, text, buttons, status = await token_get_flow(ext_api_manager, callback.from_user.id)
    kb = get_inline_kb(*buttons)
    if token:
        text = phrases.account_name
    msg = (
        await callback.message.edit_text(text=text, reply_markup=kb)
    ).message_id
    new_state = token_status_to_state.get(status, InputAccount.name)
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
    message: Message, ext_api_manager: MyExternalApiForBot, state: FSMContext
):
    kb = get_inline_kb("MENU")
    data = await state.get_data()
    msg = data.get("msg")
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
    except TelegramBadRequest:
        pass
    user = await ext_api_manager.read_user(message.from_user.id)
    master_pas = data.get("master_password")
    salt_string = user.get("salt")
    salt_bytes = base64.b64decode(salt_string.encode("utf-8"))
    password_bytes = encrypt_account_content(message.text, master_pas, salt_bytes)
    password_string = base64.b64encode(password_bytes).decode("utf-8")
    msg = data.get("msg")
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
    except TelegramBadRequest:
        pass
    msg = (await message.answer(phrases.account_params, reply_markup=kb)).message_id
    data.update(msg=msg, password_string=password_string)
    await state.set_data(data)
    await state.set_state(InputAccount.params)


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
    message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot
):
    data = await state.get_data()
    account_name = data.pop("name")
    msg = data.get("msg")
    params = data["params"]
    i = data["index"]
    buttons = ("MENU",)
    text = phrases.start
    status = ""

    if params:
        current_param = params[i]
        content = message.text
        secret = data.pop("secret", False)

        if secret:
            master_password = data.get("master_password")
            log.debug("Master Password: %s", master_password)
            salt = data.get("user_salt")
            content = make_secret(message.text, master_password, salt)

        data["collected"].append({
            "name": current_param,
            "content": content,
            "secret": secret,
        })
        i += 1
        data["index"] = i
        text = f"Введите {current_param}"
        buttons = ("MENU", "SECRET")

    if i == len(params):
        data.pop("params")
        data.pop("index")
        token, text, buttons, status = await token_get_flow(ext_api_manager, message.from_user.id)
        if token:
            await ext_api_manager.create_account(
                access_token=token,
                account_name = account_name,
                params = params
            )
            text = phrases.account_created.format(account_name)
    await delete_msg_if_exists(msg, message)
    kb = get_inline_kb(**buttons)
    msg = (await message.answer(text=text, reply_markup=kb)).message_id
    data.update(msg=msg)
    new_state = token_status_to_state.get(status, None)
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
#     acc_params_lst = data.get("acc_params_lst")
#     master_password = data.get("master_password")
#     log.debug("master password: %s", master_password)
#     if not acc_params_lst:
#         access_token = await state.storage.get_token(state.key, "access_token")
#         log.debug("token: %s", access_token)
#         acc = await ext_api_manager.read(
#             prefix="account",
#             access_token=access_token,
#             ident_val=callback.from_user.id,
#         )
#         acc_params_lst = []
#         if acc:
#             for i in acc:
#                 log.debug("acc: %s", i)
#                 acc_params_lst.append(
#                     {
#                         "name": "name",
#                         "content": i.get("name"),
#                         "secret": i.get("secret"),
#                         "acc_id": i.get("id"),
#                     }
#                 )
#                 acc_params_lst.append(
#                     {
#                         "name": "password",
#                         "content": i.get("password"),
#                         "secret": i.get("secret"),
#                         "acc_id": i.get("id"),
#                     }
#                 )
#             extra_params_lst = await ext_api_manager.read(
#                 prefix="account/params",
#                 access_token=access_token,
#                 ident="user_id",
#                 ident_val=callback.from_user.id,
#                 to_join="account",
#             )
#             if extra_params_lst is not None:
#                 extra_params_lst = [
#                     i
#                     for i in extra_params_lst
#                     if i.get("name") not in ("name", "password")
#                 ]
#                 acc_params_lst += extra_params_lst
#         data.update(acc_params_lst=acc_params_lst)
#     if acc_params_lst:
#         text = "<b>Список аккаунтов:\n</b>"
#         acc_id = acc_params_lst[0].get("acc_id")
#         text += f"account with id: {acc_id}:\n"
#         for param in acc_params_lst:
#             if param.get("secret") or param.get("name") == "password":
#                 encrypted_bytes = base64.urlsafe_b64decode(param.get("content"))
#                 text += phrases.params_list.format(
#                     param.get("name"),
#                     decrypt_account_content(encrypted_bytes, master_password),
#                 )
#             else:
#                 text += phrases.params_list.format(
#                     param.get("name"), param.get("content")
#                 )
#     else:
#         text = "<b>\t\t\tСписок аккаунтов пуст</b>"
#     kb = get_inline_kb("MENU")
#     msg = (await callback.message.edit_text(text=text, reply_markup=kb)).message_id
#     data.update(msg=msg)
#     await state.set_data(data)
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
