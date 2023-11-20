import os

from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_KEY = os.environ.get("TELEGRAM_BOT_KEY")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
DEFAULT_CATEGORIES = os.environ.get("DEFAULT_CATEGORIES").split(";")
SUPERUSER_IDS = os.environ.get("SUPERUSER_IDS").split(";")
WHITE_LIST = os.environ.get("WHITE_LIST").split(";")
