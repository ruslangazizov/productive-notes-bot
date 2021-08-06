from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import category_callback


show_all_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Показать все",
                             callback_data=category_callback.new(category_name="show_all_button"))
    ]
])
