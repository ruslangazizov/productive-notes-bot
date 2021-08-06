from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import confirmation_callback

categories_actions = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Удалить категорию",
                             callback_data=confirmation_callback.new(action_name="delete")),
        InlineKeyboardButton("Добавить категорию",
                             callback_data=confirmation_callback.new(action_name="add"))
    ]
])

confirmation_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Да", callback_data=confirmation_callback.new(action_name="yes")),
        InlineKeyboardButton("Нет", callback_data=confirmation_callback.new(action_name="no"))
    ]
])
