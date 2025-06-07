import logging
from aiogram import Router, F
from bot.filters import CallbackPasswordFactory
from aiogram.types import CallbackQuery, Message
from bot.utils import ExternalApi, get_inline_kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from bot.lexicon import phrases
from core.security import get_password_from_hash, get_password_hash
from bot.filters.states import CreateAcc

router = Router()

log = logging.getLogger('app.bot.handlers')

@router.callback_query(StateFilter(default_state), CallbackPasswordFactory.filter(F.act.lower() == 'accounts'))
async def process_button_accounts(callback: CallbackQuery, callback_data: CallbackPasswordFactory,
                                  ext_api_manager: ExternalApi, state: FSMContext):
    await callback.answer()
    try:
        accounts = list(await ext_api_manager.read(prefix='accounts', ident=callback.from_user.id))
    except TypeError:
        accounts = list()

    text=''
    for i in accounts:
        password = get_password_from_hash(i.get('password'))
        text += phrases.accounts.format(i.get('resource'), password)

    msg = (await state.get_data()).get('msg')
    await callback.bot.edit_message_text(chat_id=callback.chat.it, message_id=msg, text=text)

@router.callback_query(StateFilter(default_state), CallbackPasswordFactory.filter(F.act.lower() == 'create account'))
async def process_create_account(callback: CallbackQuery, callback_data: CallbackPasswordFactory, state: FSMContext):
    await callback.answer()
    kb = get_inline_kb('MENU', user_id=callback.from_user.id)
    await callback.message.edit_text(text=phrases.resource, reply_markup=kb)
    await state.set_state(CreateAcc.resource)

@router.message(StateFilter(CreateAcc.resource))
async def process_input_resource(message: Message, state: FSMContext):
    await state.update_data(resource=message.text)
    await message.delete()
    msg = (await state.get_data()).get('msg')
    kb = get_inline_kb('MENU', user_id=message.from_user.id)
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg, text=phrases.resource_password, reply_markup=kb)
    await state.set_state(CreateAcc.password)

@router.message(StateFilter(CreateAcc.password))
async def process_input_resource(message: Message, state: FSMContext, ext_api_manager: ExternalApi):
    data = await state.get_data()
    password = get_password_hash(message.text)
    acc_id = await ext_api_manager.create(prefix='account', resource=data.get('resource'), password=password)
    log.info('аккаунт: %s создан', acc_id)
    data.pop('resource')
    await state.clear()
    await state.update_data(data)