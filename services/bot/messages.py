
async def delete_msg_if_exists(message_id, message, exc=Exception):
    if message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except exc:
            pass

async def set_previous_data(redis_service, state, user_id, text: str | None = None, buttons = None):
    previous_data = {"previous_state": state}
    if text is not None:
        previous_data.update(previous_text=text)
    if buttons is not None:
        previous_data.update(previous_buttos=buttons)
    await redis_service.set(f"{user_id}:previous_data")
