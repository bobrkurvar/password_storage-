async def delete_msg_if_exists(message_id, message, exc=Exception):
    if message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except exc:
            pass