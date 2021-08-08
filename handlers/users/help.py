from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def show_bot_help(message: types.Message):
    text = ('"Когда вам в голову пришла хорошая идея, действуйте незамедлительно" - Билл Гейтс',
            "",
            "Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку",
            "/menu - Показать главное меню")
    
    await message.answer("\n".join(text))
