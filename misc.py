from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TELEGRAM_BOT_KEY, WHITE_LIST, SUPERUSER_IDS


def user_is_whitelisted(user_id):
    return str(user_id) in WHITE_LIST


def user_is_superuser(user_id):
    return str(user_id) in SUPERUSER_IDS


bot = Bot(token=TELEGRAM_BOT_KEY)
dp = Dispatcher(bot, storage=MemoryStorage())
