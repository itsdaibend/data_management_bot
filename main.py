from aiogram import types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext

import database
from bot_logging import *
from handlers.categories import *
from handlers.subcategories import *
from handlers.childcategories import *
from forms import EditDataEntryForm
from keyboards import main_keyboard
from misc import *
from models import (
    ChildCategoryData,
    SubCategoryData,
    User,
    CategoryData,
)


async def on_startup():
    await database.setup()


@dp.message_handler(commands=["start"])
async def start_chat(message: types.Message):
    if not user_is_whitelisted(message.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {message.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await message.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    current_user = await User.get_or_none(user_id=message.from_user.id)

    if current_user:
        await User.filter(user_id=message.from_user.id).update(
            is_superuser=user_is_superuser(message.from_user.id)
        )
    else:
        current_user = await User.create(
            user_id=message.from_user.id,
            is_superuser=user_is_superuser(message.from_user.id),
        )
        logging.info(
            f"User {message.from_user.id} has been registered. Is superuser? - {current_user.is_superuser}"
        )
    logging.info(f"User {message.from_user.id} started bot.")

    await message.answer(
        f"<b>Вас вітає навчальний бот TORTS.UA!</b>\n\nTORTS.UA – виробник смаколиків із власною мережею затишних, сучасних магазинів біля дому. Працюємо з 2019 року.\n\nНаш Сайт https://www.torts.ua/\nМи у Instagram <a href='https://www.instagram.com/torts.ua/'>@torts.ua</a>\nМи у Facebook <a href='https://www.facebook.com/torts.ua/'>@torts.ua</a>\nЧат-бот для відгуків @TORTSUA_bot\nГаряча лінія (067) 077-87-88",
        parse_mode="html",
        reply_markup=await main_keyboard(message.from_user.id),
        disable_web_page_preview=True,
    )


@dp.callback_query_handler(lambda query: query.data == "main_menu")
async def main_menu(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    await bot.send_message(
        query.from_user.id,
        "Оберіть категорію:",
        reply_markup=await main_keyboard(query.from_user.id),
    )


@dp.callback_query_handler(lambda query: query.data.startswith("edit_data_entry_"))
async def edit_data_entry_text(query: types.CallbackQuery, state: FSMContext):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    user_id = query.from_user.id
    if not user_is_superuser(user_id):
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )
        return

    category_type = query.data.split("_")[3]
    data_entry_id = int(query.data.split("_")[4])

    await bot.send_message(user_id, "Відредагуйте дані та надішліть змінений текст:")
    await EditDataEntryForm.WaitingForNewDataEntryText.set()
    await state.update_data(category_type=category_type, data_entry_id=data_entry_id)


@dp.message_handler(state=EditDataEntryForm.WaitingForNewDataEntryText)
async def process_new_data_entry_text(message: types.Message, state: FSMContext):
    if not user_is_whitelisted(message.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {message.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await message.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    user_id = message.from_user.id
    if not user_is_superuser(user_id):
        await bot.send_message(user_id, text="⛔️ У вас немає дозволу на цю дію.")
        await state.finish()
        return

    message_data = message.text
    if not message_data:
        await bot.send_message(user_id, "Ви не відправили змінений текст.")
    else:
        category_type = (await state.get_data())["category_type"]
        data_entry_id = (await state.get_data())["data_entry_id"]

        if category_type == "childcategory":
            data_instance = await ChildCategoryData.get_or_none(id=data_entry_id)
        elif category_type == "subcategory":
            data_instance = await SubCategoryData.get_or_none(id=data_entry_id)
        elif category_type == "category":
            data_instance = await CategoryData.get_or_none(id=data_entry_id)

        data_instance.file_id = message_data
        await data_instance.save()

        await bot.send_message(user_id, "Дані було змінено.")
        logging.info(f"User {message.from_user.id} edited {category_type} data entry.")

    await state.finish()


if __name__ == "__main__":
    executor.start(dp, on_startup())
    executor.start_polling(dp, skip_updates=True)
