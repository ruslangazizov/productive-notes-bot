from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def show_bot_help(message: types.Message):
    text = ("Этот бот создан пользователем @etimesoy для удобного и быстрого сохранения "
            "идей и мыслей в удобном формате в любимом мессенджере😉",
            "Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")
    
    await message.answer("\n".join(text))
