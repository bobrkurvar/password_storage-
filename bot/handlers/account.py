from aiogram import Router, F
from bot.filters import CallbackFactory
from bot.filters.states import InputAccount
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from bot.utils.keyboards import get_inline_kb
from utils.external import MyExternalApiForBot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from bot.lexicon import phrases
from core.security import encrypt, decrypt
import logging
import base64


router = Router()
log = logging.getLogger(__name__)

@router.callback_query(StateFilter(default_state), CallbackFactory.filter(F.act.lower()=='create account'))
async def process_create_account(callback: CallbackQuery, state: FSMContext):
    kb = get_inline_kb('MENU')
    msg = (await callback.message.edit_text(text=phrases.account_params, reply_markup=kb)).message_id
    await state.set_state(InputAccount.params)
    await state.update_data(msg=msg)

@router.message(StateFilter(InputAccount.params, InputAccount.input))
async def process_select_account_params(message: Message, state: FSMContext, ext_api_manager):
    data = await state.get_data()
    cur_state = await state.get_state()
    msg = data.get('msg')
    if cur_state == InputAccount.params:
        params_lst = message.text.split()
        if not ('password' in params_lst):
            params_lst.append('password')
        data.update(params_lst=params_lst)
    else:
        params_lst = data.get('params_lst')
        params_dict_lst = data.get('params_dict_lst', [])
        if params_lst:
            content = message.text
            cur_param = params_lst[0]
            log.debug('current param: %s', cur_param)
            if data.pop('secret', None):
                master_password = (await ext_api_manager.read(prefix='user', ident_val=message.from_user.id))[0].get('password')
                content = base64.urlsafe_b64encode(encrypt(message.text, master_password)).decode()
            param_dict = dict(name=cur_param, content=content)
            log.debug('param dict: %s', param_dict)
            params_dict_lst.append(param_dict)
            log.debug('params dict list: %s', params_dict_lst)
            params_lst = params_lst[1:]
            if params_lst:
                data.update(params_lst=params_lst, params_dict_lst=params_dict_lst)
            else:
                data.pop('params_lst')
                access_token = await state.storage.get_token(state.key, "access_token")
                acc_id = await ext_api_manager.create(prefix='account', access_token=access_token, user_id=message.from_user.id)
                log.debug('params: %s', params_dict_lst)
                await ext_api_manager.create(prefix='account/params', access_token=access_token, acc_id=acc_id, items=params_dict_lst)
                data.pop('params_dict_lst')
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
    except TelegramBadRequest:
        pass
    if params_lst:
        cur_par = params_lst[0]
        kb = get_inline_kb('MENU', 'SECRET')
        text = f'Введите {cur_par}'
        await state.set_state(InputAccount.input)
    else:
        kb = get_inline_kb('MENU')
        text = phrases.account_created
        await state.set_state(None)
    msg = (await message.answer(text=text, reply_markup=kb)).message_id
    data.update(msg=msg)
    await state.set_data(data)

@router.callback_query(StateFilter(InputAccount.params, InputAccount.input), CallbackFactory.filter(F.act.lower() == 'secret'))
async def press_button_secret_param(callback: CallbackQuery, state: FSMContext):
    cur_par = (await state.get_data()).get('params_lst')[0]
    kb = get_inline_kb('MENU')
    msg = (await callback.message.edit_text(text=f'Введите {cur_par}', reply_markup=kb)).message_id
    await state.update_data(msg=msg, secret=True)

# @router.message(StateFilter(InputAccount.input))
# async def process_input_account_params(message: Message, state: FSMContext):
#     data = await state.get_data()
#     msg = data.get('msg')
#     params_lst = data.get('params_lst')


# @router.message(StateFilter(InputAccount.name))
# async def process_input_account_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     msg = (await state.get_data()).get('msg')
#     kb = get_inline_kb('MENU')
#     try:
#         await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
#     except TelegramBadRequest:
#         pass
#     msg = (await message.answer(text=phrases.account_password, reply_markup=kb)).message_id
#     await state.update_data(msg=msg)
#     await state.set_state(InputAccount.password)



# @router.message(StateFilter(InputAccount.password))
# async def process_input_account_password(message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot):
#     data = await state.get_data()
#     msg = data.get('msg')
#     name = data.pop('name')
#     data.pop('acc_lst', None)
#     access_token = await state.storage.get_token(state.key, "access_token")
#     master_password = (await ext_api_manager.read(prefix='user', ident_val=message.from_user.id))[0].get('password')
#     enc_pass = base64.urlsafe_b64encode(encrypt(message.text, master_password)).decode()
#     account = await ext_api_manager.create(prefix='account', access_token=access_token, resource=name,
#                                            password=enc_pass, user_id=message.from_user.id)
#     kb = get_inline_kb('MENU')
#     try:
#         await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
#     except TelegramBadRequest:
#         pass
#     msg = (await message.answer(text=phrases.account_created.format(account), reply_markup=kb)).message_id
#     data.update(msg=msg)
#     await state.set_data(data)
#     await state.set_state(None)

@router.callback_query(StateFilter(default_state), CallbackFactory.filter(F.act.lower() == 'accounts'))
async def press_button_accounts(callback: CallbackQuery, ext_api_manager: MyExternalApiForBot, state: FSMContext):
    data = await state.get_data()
    acc_lst = data.get('acc_lst')
    access_token = await state.storage.get_token(state.key, "access_token")
    master_password = (await ext_api_manager.read(prefix='user', ident_val=callback.from_user.id))[0].get('password')
    log.debug('token: %s', access_token)
    if not acc_lst:
        acc_lst = await ext_api_manager.read(prefix='account', access_token=access_token)
        await state.update_data(acc_lst=acc_lst)
    if acc_lst:
        text = '<b>Список аккаунтов:\n</b>'
        for acc in acc_lst:
            encrypted_bytes = base64.urlsafe_b64decode(acc.get('password'))
            text += phrases.account_list.format(acc.get('resource'), decrypt(encrypted_bytes, master_password))
    else:
        text='<b>\t\t\tСписок аккаунтов пуст</b>'
    kb = get_inline_kb('MENU')
    await callback.message.edit_text(text=text, reply_markup=kb)

# @router.message(Command(commands=['delete',]))
# async def process_command_delete(message: Message, ext_api_manager: MyExternalApiForBot, state: FSMContext):
#     name = message.get_args()
#     await ext_api_manager.remove(prefix='account', ident='resource', ident_val=name)
#     kb = get_inline_kb('MENU')
#     msg = (await state.get_data()).get('msg')
#     try:
#         await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
#     except TelegramBadRequest:
#         pass
#     await message.answer(text='', reply_markup=kb)


