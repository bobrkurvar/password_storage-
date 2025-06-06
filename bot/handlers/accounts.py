from aiogram import Router, F
from bot.filters import CallbackPasswordFactory
from aiogram.types import CallbackQuery
from bot.utils import ExternalApi
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter

router = Router()



# @router.callback_query(CallbackPasswordFactory.filter(F.act.lower() == 'accounts'))
# async def process_button_accounts(callback: CallbackQuery, callback_data: CallbackPasswordFactory,
#                                   ext_api_manager: MyExternalApiForBot):
#     await callback.answer()
#     accounts = (await ext_api_manager.read(prefix='accounts', ident='user_id', ident_val=''))
