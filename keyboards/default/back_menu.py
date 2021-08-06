from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton("Главное меню"), KeyboardButton("Назад")
    ]
], resize_keyboard=True)
