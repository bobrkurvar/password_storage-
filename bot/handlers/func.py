from aiogram.fsm.context import FSMContext
from bot.filters.states import InputUser
from aiogram.types import Message, CallbackQuery
from bot.lexicon import phrases
from bot.utils import get_inline_kb

async def get_auth(callback: CallbackQuery | None, message: Message | None, state: FSMContext):
    token = (await state.get_data()).get('token')
    msg = (await state.get_data()).get('msg')
    if token:
        await state.update_data(token=token)
    else:
        kb = get_inline_kb('MENU')
        if message:
            msg = await message.bot.send_message(chat_id=message.chat.id, text=phrases.password, reply_markup=kb) if not msg else await  message.bot.edit_message_text(chat_id=message.chat.id,  message_id=msg,                                                                                                                                                   text=phrases.password, reply_markup=kb)
            msg = msg.message_id
        elif callback:
            await callback.answer()
            msg = await callback.message.edit_text(text=phrases.password, reply_markup=kb)
            msg = msg.message_id
        await state.update_data(msg=msg)
        await state.set_state(InputUser.password)

