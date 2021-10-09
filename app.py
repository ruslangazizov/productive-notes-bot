import logging

from aiogram import executor
from aiogram.utils.executor import start_webhook

from data import config
from loader import dp, db, bot
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Подключаемся к webhook
    # logging.info("Подключаемся к webhook")
    # logging.info(f"{config.WEBHOOK_URL=}")
    # await bot.set_webhook(url=config.WEBHOOK_URL, certificate=SSL_CERTIFICATE)

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
    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=config.WEBHOOK_PATH,
    #     on_startup=on_startup,
    #     host=config.WEBHOOK_HOST,
    #     port=config.WEBAPP_PORT,
    #     ssl_context=ssl_context
    # )
