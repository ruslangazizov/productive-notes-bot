from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton("Удалить заметку"), KeyboardButton("Добавить заметку")
    ],
    [
        KeyboardButton("Изменить заметку"), KeyboardButton("Посмотреть заметки")
    ],
    [
        KeyboardButton("Категории")
    ]
], resize_keyboard=True)
