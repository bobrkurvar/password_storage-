from aiogram import Router, F
from bot.filters import CallbackFactory
from bot.filters.states import InputAccount, InputUser
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from bot.utils.keyboards import get_inline_kb
from utils.external import MyExternalApiForBot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from bot.lexicon import phrases


router = Router()

@router.callback_query(StateFilter(default_state), CallbackFactory.filter(F.act.lower()=='create account'))
async def process_create_account(callback: CallbackQuery, state: FSMContext):
#     access_token = (await state.get_data()).get('access_token')
#     if not access_token:
#         buttons = ('SIGN IN', 'SIGN UP')
#         kb = get_inline_kb(*buttons)
#         msg = (await callback.message.edit_text(text=phrases.start, reply_markup=kb)).message_id
#     else:
    kb = get_inline_kb('MENU')
    msg = (await callback.message.edit_text(text=phrases.account_name, reply_markup=kb)).message_id
    await state.set_state(InputAccount.name)
    await state.update_data(msg=msg)

@router.message(StateFilter(InputAccount.name))
async def process_input_account_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    msg = (await state.get_data()).get('msg')
    kb = get_inline_kb('MENU')
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
    except TelegramBadRequest:
        pass
    msg = (await message.answer(text=phrases.account_password, reply_markup=kb)).message_id
    await state.update_data(msg=msg)
    await state.set_state(InputAccount.password)

@router.message(StateFilter(InputAccount.password))
async def process_input_account_password(message: Message, state: FSMContext, ext_api_manager: MyExternalApiForBot):
    data = await state.get_data()
    msg = data.get('msg')
    name = data.pop('name')
    access_token = (await state.get_data()).get('access_token')
    account = await ext_api_manager.create(prefix='account', access_token=access_token, resource=name, password=message.text, user_id=message.from_user.id)
    if account is None:
        refresh_token = (await state.get_data()).get('refresh_token')
        if refresh_token:
            tokens = await ext_api_manager.refresh(refresh_token)
            access_token, refresh_token = tokens.get('access_token'), tokens.get('refresh_token')
            access_time, refresh_time = 900, 86400*7
            await state.update_data(access_token=access_token, ttl=access_time)
            await state.update_data(refresh_token=refresh_token, ttl=refresh_time)
            account = await ext_api_manager.create(prefix='account', access_token=access_token, resource=name,
                                                   password=message.text, user_id=message.from_user.id)
        else:
            data.pop('access_token')
            data.pop('refresh_token')

    kb = get_inline_kb('MENU')
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg)
    except TelegramBadRequest:
        pass
    msg = (await message.answer(text=phrases.account_created.format(account), reply_markup=kb)).message_id
    data.update(msg=msg)
    await state.set_data(data)
    await state.set_state(None)

@router.callback_query(StateFilter(default_state), CallbackFactory.filter(F.act.lower() == 'accounts'))
async def press_button_accounts(callback: CallbackQuery, ext_api_manager: MyExternalApiForBot, state: FSMContext):
    data = await state.get_data()
    acc_lst = data.get('acc_lst')
    access_token=data.get('access_token')
    if not acc_lst:
        acc_lst = await ext_api_manager.read(prefix='account', access_token=access_token)
        await state.update_data(acc_lst=acc_lst)
    if acc_lst:
        text = '<b>Список аккаунтов:\n</b>'
        for acc in acc_lst:
            text += phrases.account_list.format(acc.get('resource'), acc.get('password'))
    else:
        text='<b>\t\t\tСписок аккаунтов пуст</b>'
    kb = get_inline_kb('MENU')
    await callback.message.edit_text(text=text, reply_markup=kb)
