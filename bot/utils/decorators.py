from aiogram.fsm.context import FSMContext
from bot.filters.states import InputUser
from aiogram.types import Message, CallbackQuery
from bot.lexicon import phrases
from bot.utils import get_inline_kb
from functools import wraps


def get_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        state = kwargs.get('state')
        ext_api_manager = kwargs.get('ext_api_manager')
        token = (await state.get_data()).get('token')
        msg = (await state.get_data()).get('msg')
        if token:
            await state.update_data(token=token)
            await func(*args, **kwargs)
        else:
            message = next((i for i in args if isinstance(i, Message)), None)
            kb = get_inline_kb('MENU')
            if message:
                if await ext_api_manager.read(prefix='user', id=message.from_user.id):
                    text=phrases.login
                    await state.set_state(InputUser.password)
                else:
                    await state.set_state(InputUser.new_password)
                    text = phrases.reg
                msg = await message.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=kb) if not msg else await  message.bot.edit_message_text(chat_id=message.chat.id,  message_id=msg,                                                                                                                                                   text=phrases.password, reply_markup=kb)
                msg = msg.message_id
            else:
                callback = next((i for i in args if isinstance(i, CallbackQuery)), None)
                await callback.answer()
                if await ext_api_manager.read(prefix='user', id=callback.from_user.id):
                    text = phrases.login
                    await state.set_state(InputUser.password)
                else:
                    await state.set_state(InputUser.new_password)
                    text = phrases.reg
                msg = await callback.message.edit_text(text=text, reply_markup=kb)
                msg = msg.message_id
            await state.update_data(msg=msg)
    return wrapper



