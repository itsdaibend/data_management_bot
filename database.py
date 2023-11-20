from config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
    DEFAULT_CATEGORIES,
    SUPERUSER_IDS,
)
from tortoise import Tortoise
import logging

from models import Category, User


logger = logging.getLogger(__name__)

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def setup():
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas()

    existing_users = await User.all()
    if not existing_users:
        for user_id in SUPERUSER_IDS:
            user = await User.create(user_id=user_id, is_superuser=True)
            logger.info(f"Administrator user has been created: {user.user_id}")

    existing_categories = await Category.all()
    if not existing_categories:
        for category_name in DEFAULT_CATEGORIES:
            category = await Category.create(
                name=category_name, owner_id=SUPERUSER_IDS[0]
            )
            logger.info(f"New category has been created: {category.name}")

    await Tortoise.close_connections()
