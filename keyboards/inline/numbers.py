from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import number_callback


def get_number_buttons(start_number: int, number_of_buttons: int, additional_button: str = None) -> InlineKeyboardMarkup:
    number_buttons = InlineKeyboardMarkup(row_width=3)
    for number in range(start_number, start_number + number_of_buttons):
        category_button = InlineKeyboardButton(text=str(number),
                                               callback_data=number_callback.new(value=str(number)))
        number_buttons.insert(category_button)
    if additional_button:
        button = InlineKeyboardButton(text=additional_button,
                                      callback_data=number_callback.new(value=additional_button))
        number_buttons.insert(button)
    return number_buttons
