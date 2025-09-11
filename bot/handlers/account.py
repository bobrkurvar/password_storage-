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
from core.security import decrypt, encrypt
from utils.external import MyExternalApiForBot

router = Router()
log = logging.getLogger(__name__)


@router.callback_query(
    StateFilter(default_state),
    CallbackFactory.filter(F.act.lower() == "create account"),
)
async def process_create_account(callback: CallbackQuery, state: FSMContext):
    kb = get_inline_kb("MENU")
    msg = (
        await callback.message.edit_text(text=phrases.account_params, reply_markup=kb)
    ).message_id
    await state.set_state(InputAccount.params)
    await state.update_data(msg=msg)


@router.message(StateFilter(InputAccount.params, InputAccount.input))
async def process_select_account_params(
    message: Message, state: FSMContext, ext_api_manager
):
    data = await state.get_data()
    cur_state = await state.get_state()
    msg = data.get("msg")
    if cur_state == InputAccount.params:
        params_lst = message.text.split()
        if not ("password" in params_lst):
            params_lst.append("password")
        data.update(params_lst=params_lst)
    else:
        params_lst = data.get("params_lst")
        params_dict_lst = data.get("params_dict_lst", [])
        if params_lst:
            content = message.text
            cur_param = params_lst[0]
            log.debug("current param: %s", cur_param)
            param_dict = dict(secret=False)
            if data.pop("secret", None):
                master_password = (
                    await ext_api_manager.read(
                        prefix="user", ident_val=message.from_user.id
                    )
                ).get("password")
                log.debug('Master Password: %s', master_password)
                content = base64.urlsafe_b64encode(
                    encrypt(message.text, master_password)
                ).decode()
                param_dict.update(secret=True)
            param_dict.update(name=cur_param, content=content)
            log.debug("param dict: %s", param_dict)
            params_dict_lst.append(param_dict)
            log.debug("params dict list: %s", params_dict_lst)
            params_lst = params_lst[1:]
            if params_lst:
                data.update(params_lst=params_lst, params_dict_lst=params_dict_lst)
            else:
                data.pop("params_lst")
                access_token = await state.storage.get_token(state.key, "access_token")
                acc_id = (await ext_api_manager.create(
                    prefix="account",
                    access_token=access_token,
                    user_id=message.from_user.id,
                )).get('id')
                log.debug("params: %s", params_dict_lst)
                log.debug('acc_id: %s', acc_id)
                await ext_api_manager.create(
                    prefix="account/params",
                    access_token=access_token,
                    acc_id=acc_id,
                    items=params_dict_lst,
                )
                data.pop("params_dict_lst")
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
    except TelegramBadRequest:
        pass
    if params_lst:
        cur_par = params_lst[0]
        kb = get_inline_kb("MENU", "SECRET")
        text = f"Введите {cur_par}"
        await state.set_state(InputAccount.input)
    else:
        kb = get_inline_kb("MENU")
        text = phrases.account_created
        await state.set_state(None)
    msg = (await message.answer(text=text, reply_markup=kb)).message_id
    data.update(msg=msg)
    data.pop("acc_params_lst", None)
    await state.set_data(data)


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


@router.callback_query(
    StateFilter(default_state), CallbackFactory.filter(F.act.lower() == "accounts")
)
async def press_button_accounts(
    callback: CallbackQuery, ext_api_manager: MyExternalApiForBot, state: FSMContext
):
    data = await state.get_data()
    acc_params_lst = data.get("acc_params_lst")
    master_password = (
        await ext_api_manager.read(prefix="user", ident_val=callback.from_user.id)
    ).get("password")
    if not acc_params_lst:
        access_token = await state.storage.get_token(state.key, "access_token")
        log.debug("token: %s", access_token)
        acc_params_lst = await ext_api_manager.read(
            prefix="account/params",
            access_token=access_token,
            ident="user_id",
            ident_val=callback.from_user.id,
            to_join="account",
        )
        data.update(acc_params_lst=acc_params_lst)
    if acc_params_lst:
        text = "<b>Список аккаунтов:\n</b>"
        acc_id = acc_params_lst[0].get("acc_id")
        text += f"account with id: {acc_id}:\n"
        for param in acc_params_lst:
            if param.get("acc_id") == acc_id:
                if param.get("secret"):
                    encrypted_bytes = base64.urlsafe_b64decode(param.get("content"))
                    text += phrases.params_list.format(
                        param.get("name"), decrypt(encrypted_bytes, master_password)
                    )
                else:
                    text += phrases.params_list.format(
                        param.get("name"), param.get("content")
                    )
            else:
                acc_id = param.get("acc_id")
                text += f"\n\naccount with id: {acc_id}:\n"
                if param.get("secret"):
                    encrypted_bytes = base64.urlsafe_b64decode(param.get("content"))
                    text += phrases.params_list.format(
                        param.get("name"), decrypt(encrypted_bytes, master_password)
                    )
                else:
                    text += phrases.params_list.format(
                        param.get("name"), param.get("content")
                    )
    else:
        text = "<b>\t\t\tСписок аккаунтов пуст</b>"
    kb = get_inline_kb("MENU")
    msg = (await callback.message.edit_text(text=text, reply_markup=kb)).message_id
    data.update(msg=msg)
    await state.set_data(data)
