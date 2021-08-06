from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import category_callback
from data import DEFAULT_CATEGORIES


def get_categories_buttons(*additional_buttons: str, categories: List[str] = None) -> InlineKeyboardMarkup:
    if categories is None:
        categories = DEFAULT_CATEGORIES
    categories_buttons = InlineKeyboardMarkup(row_width=2)
    for category in categories:
        category_button = InlineKeyboardButton(text=category,
                                               callback_data=category_callback.new(category_name=category))
        categories_buttons.insert(category_button)
    for button in additional_buttons:
        button = InlineKeyboardButton(text=button,
                                      callback_data=category_callback.new(category_name=button))
        categories_buttons.insert(button)
    return categories_buttons
