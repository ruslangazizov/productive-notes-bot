import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from data import config
from utils.db_api.postgres import Database

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2()
dp = Dispatcher(bot, storage=storage)

loop = asyncio.get_event_loop()
db = loop.run_until_complete(Database.create_pool())
