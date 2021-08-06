import logging

from aiogram import Dispatcher

from data.config import ADMINS


async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот Запущен")

        except Exception as err:
            logging.exception(err)


async def on_user_press_start_notify(dp: Dispatcher, user_id: int):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, f"Пользователь @{user_id} запустил бота")

        except Exception as err:
            logging.exception(err)
