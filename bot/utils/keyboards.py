import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.dialog.callback import CallbackFactory

log = logging.getLogger(__name__)

# def get_simple_inline_kb(
#     *buttons_texts, width: int = 1
# ) -> InlineKeyboardMarkup:
#     kb_builder = InlineKeyboardBuilder()
#     buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(text=i) for i in buttons_texts]
#     kb_builder.row(*buttons, width=width)
#     return kb_builder.as_markup()
#
#
# def get_inline_kb_with_callback_data(
#     buttons: list[dict], width: int = 1
# ):
#     kb_builder = InlineKeyboardBuilder()
#     result_buttons: list[InlineKeyboardButton] = []
#     for button_data in buttons:
#         text = button_data.pop("text")
#         switch = button_data.pop("switch", False)
#         button = InlineKeyboardButton(
#             text=text, callback_data=CallbackFactory(**button_data).pack(), switch_inline_query=""
#         ) if switch else InlineKeyboardButton(
#             text=text, callback_data=CallbackFactory(**button_data).pack()
#         )
#         result_buttons.append(button)
#     kb_builder.row(*buttons, width=width)
#     return kb_builder.as_markup()

def get_inline_kb(
    *buttons, width: int = 1
):
    kb_builder = InlineKeyboardBuilder()
    result_buttons: list[InlineKeyboardButton] = []
    log.debug("buttons: %s", buttons)
    for button_data in buttons:
        try:
            text = button_data.pop("text")
            switch = button_data.pop("switch", False)
            button_data["act"] = text
            log.debug("without exception")
            log.debug("switch: %s", switch)
            button = InlineKeyboardButton(
                text=text, switch_inline_query_current_chat=switch + " "
            ) if switch else InlineKeyboardButton(
                text=text, callback_data=CallbackFactory(**button_data).pack()
            )
        except AttributeError:
            log.debug("with exception")
            data = {"act": button_data}
            log.debug("data: %s", data)
            button = InlineKeyboardButton(
                text=button_data, callback_data=CallbackFactory(**data).pack()
            )
        result_buttons.append(button)
    kb_builder.row(*result_buttons, width=width)
    return kb_builder.as_markup()



# def get_inline_kb(
#     *button_texts, width: int = 1, buttons_data_lst: list = None, **button_data
# ) -> InlineKeyboardMarkup:
#     kb_builder = InlineKeyboardBuilder()
#     buttons: list[InlineKeyboardButton] = []
#     for index, i in enumerate(button_texts):
#         if not buttons_data_lst:
#             data = dict(button_data)
#             data.setdefault("act", i)
#             button = InlineKeyboardButton(
#                 text=i, callback_data=CallbackFactory(**data).pack()
#             )
#         else:
#             try:
#                 data = buttons_data_lst[index]
#             except IndexError:
#                 data = {}
#             data.setdefault("act", i)
#             log.debug("data: %s", data)
#             button = InlineKeyboardButton(
#                 text=i, callback_data=CallbackFactory(**data).pack()
#             )
#         buttons.append(button)
#     kb_builder.row(*buttons, width=width)
#     return kb_builder.as_markup()
