from aiogram.fsm.context import FSMContext

# def miss_msg_cache(func):
#     async def wrapper(state: FSMContext):
#         msg = (await state.get_data()).get('msg')
#         await state.update_data(msg=msg.message_id)
#         await func()
#     return wrapper