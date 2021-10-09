import ssl

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from data import config
from utils.db_api.postgres import Database

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# webhook_cert = open(config.WEBHOOK_SSL_CERT, "rb")
# SSL_CERTIFICATE = webhook_cert.read()
# webhook_cert.close()
# ssl_context.load_cert_chain(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV)
