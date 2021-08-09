import logging

from aiogram import executor

from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Создать подключение к базе данных
    logging.info("Создаем подключение к базе данных")
    await db.create_pool()

    # Создать стандартные таблицы, если такие еще не была созданы
    logging.info("Создаем таблицы: для пользователей, заметок и категорий")
    await db.create_standard_tables()

    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    logging.info("Уведомляем админов о том, что бот запустился")
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
