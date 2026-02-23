import asyncio

async def delete_msg_if_exists(message_id, message, exc=Exception):
    if message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=message_id
            )
        except exc:
            pass


DEBOUNCE_DELAY = 1
USER_PENDING_TASKS = {}

async def delayed_search(ext_api_manager, user_id: int, search_query: str, access_token: str):
    await asyncio.sleep(DEBOUNCE_DELAY)
    return await ext_api_manager.search_full_text(user_id=user_id, search_query=search_query, access_token=access_token)