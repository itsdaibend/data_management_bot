from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards import (
    categories_data_add_keyboard,
    categories_data_delete_keyboard,
    confirmation_category_data_delete_keyboard,
    confirmation_delete_category_keyboard,
    main_keyboard,
    subcategories_keyboard,
)
from main import user_is_superuser
from forms import CategoryDataEntryForm, CreateCategoryForm, EditCategoryForm
from models import (
    Category,
    CategoryData,
    ChildCategory,
    ChildCategoryData,
    SubCategory,
    SubCategoryData,
)
from misc import *
from bot_logging import *


@dp.callback_query_handler(lambda query: query.data.startswith("category_"))
async def show_subcategories(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    """send categories data"""
    category_id = int(query.data.split("_")[1])
    category = await Category.get_or_none(id=category_id)

    user_id = query.from_user.id

    if category:
        category_data = await CategoryData.filter(category=category)
        if category_data:
            for data_entry in category_data:
                if data_entry.file_type == "photo":
                    sent_message = await bot.send_photo(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                elif data_entry.file_type == "video":
                    sent_message = await bot.send_video(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                elif data_entry.file_type == "document":
                    sent_message = await bot.send_document(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                elif data_entry.file_type == "animation":
                    sent_message = await bot.send_animation(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                elif data_entry.file_type == "audio":
                    sent_message = await bot.send_audio(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                elif data_entry.file_type == "sticker":
                    sent_message = await bot.send_sticker(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                elif data_entry.file_type == "voice":
                    sent_message = await bot.send_voice(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                elif data_entry.file_type == "video_note":
                    sent_message = await bot.send_video_note(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                elif data_entry.file_type == "text":
                    sent_message = await bot.send_message(
                        query.from_user.id,
                        data_entry.file_id,
                    )
                if user_is_superuser(user_id):
                    deletion_keyboard = await categories_data_delete_keyboard(
                        data_entry
                    )
                    await bot.edit_message_reply_markup(
                        chat_id=sent_message.chat.id,
                        message_id=sent_message.message_id,
                        reply_markup=deletion_keyboard,
                    )
        else:
            if user_is_superuser(user_id):
                keyboard = await categories_data_add_keyboard(category_id)
                await bot.send_message(
                    query.from_user.id,
                    f"Для цієї категорії немає даних.",
                    reply_markup=keyboard,
                )

    """List of subcategories"""
    category_id = int(query.data.split("_")[1])

    selected_category = await Category.get(id=category_id)
    category_name = selected_category.name

    subcategories = await SubCategory.filter(category_id=category_id)

    previous_category = (
        await Category.filter(id__lt=category_id).order_by("-id").first()
    )
    next_category = await Category.filter(id__gt=category_id).order_by("id").first()

    message_text = category_name

    keyboard = await subcategories_keyboard(
        subcategories,
        query.from_user.id,
        category_id,
        previous_category.id if previous_category else None,
        next_category.id if next_category else None,
    )

    await bot.send_message(query.from_user.id, message_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("add_category_data_"))
async def request_file(query: types.CallbackQuery, state: FSMContext):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    category_id = int(query.data.split("_")[3])
    user_id = query.from_user.id

    await CategoryDataEntryForm.WaitingForFile.set()
    await state.update_data(category_id=category_id)

    await bot.send_message(user_id, "Будь ласка, надішліть файл або введіть текст:")


@dp.message_handler(
    content_types=types.ContentTypes.ANY, state=CategoryDataEntryForm.WaitingForFile
)
async def process_file(message: types.Message, state: FSMContext):
    if not user_is_whitelisted(message.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {message.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await message.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    async with state.proxy() as data:
        category_id = data["category_id"]

        file_type = message.content_type
        file_id = ""

        if file_type in ["photo", "audio"]:
            file_id = getattr(message, file_type)[0].file_id
        elif file_type == "sticker":
            file_id = message.sticker.file_id
        elif file_type == "voice":
            file_id = message.voice.file_id
        elif file_type == "video_note":
            file_id = message.video_note.file_id
        elif file_type == "document":
            file_id = message.document.file_id
        elif file_type == "animation":
            file_id = message.animation.file_id
        elif file_type == "video":
            file_id = message.video.file_id
        elif file_type == "text":
            file_id = message.text

        user_id = message.from_user.id

        new_data_entry = await CategoryData.create(
            category_id=category_id,
            file_id=file_id,
            file_type=file_type,
            created_by=user_id,
        )

        keyboard = await categories_data_add_keyboard(category_id)
        await bot.send_message(
            user_id, f"Додано новий запис: Тип - {file_type}.", reply_markup=keyboard
        )
        logging.info(
            f"User {message.from_user.id} added Category data, type - '{file_type}' ."
        )

    await state.finish()


@dp.callback_query_handler(
    lambda query: query.data.startswith("categories_delete_data_")
)
async def delete_data(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    data_entry_id = int(query.data.split("_")[3])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        keyboard = await confirmation_category_data_delete_keyboard(data_entry_id)

        await bot.send_message(
            user_id,
            "Чи дійсно ви бажаєте видалити цей файл?",
            reply_markup=keyboard,
        )
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.callback_query_handler(
    lambda query: query.data.startswith("confirm_category_delete_data_")
)
async def confirm_delete_data(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    data_entry_id = int(query.data.split("_")[4])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        data_entry = await CategoryData.get_or_none(id=data_entry_id)

        if data_entry:
            await data_entry.delete()
            await bot.send_message(user_id, "Дані було видалено.")
            logging.info(f"User {query.from_user.id} deleted category data entry.")
        else:
            await bot.send_message(user_id, "Помилка: Дані не знайдено.")
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.callback_query_handler(lambda query: query.data == "new_category")
async def create_new_category(query: types.CallbackQuery):
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

    await bot.answer_callback_query(query.id)  # To close the pop-up notification

    await bot.send_message(user_id, "Введіть назву нової категорії:")
    await CreateCategoryForm.WaitingForNewCategoryName.set()


@dp.callback_query_handler(lambda query: query.data.startswith("edit_category_name_"))
async def edit_existing_category_name(query: types.CallbackQuery, state: FSMContext):
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

    category_id = int(query.data.split("_")[3])

    await bot.answer_callback_query(query.id)  # To close the pop-up notification

    await bot.send_message(user_id, "Введіть нову назву для цієї категорії:")
    await EditCategoryForm.WaitingForNewCategoryName.set()
    await state.update_data(selected_category_id=category_id)


@dp.message_handler(state=CreateCategoryForm.WaitingForNewCategoryName)
async def process_new_category_name(message: types.Message, state: FSMContext):
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

    new_category_name = message.text
    if not new_category_name:
        await bot.send_message(user_id, "Ви не ввели назву нової категорії.")
    else:
        await Category.create(name=new_category_name, owner_id=user_id)
        await bot.send_message(
            user_id,
            f"Створено нову категорію: {new_category_name}",
            reply_markup=await main_keyboard(user_id),
        )
        logging.info(
            f"User {message.from_user.id} created new category - '{new_category_name}'"
        )

    await state.finish()


@dp.message_handler(state=EditCategoryForm.WaitingForNewCategoryName)
async def process_new_category_name(message: types.Message, state: FSMContext):
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

    new_category_name = message.text
    if not new_category_name:
        await bot.send_message(user_id, "Ви не ввели назву нової категорії.")
    else:
        category_id = (await state.get_data())["selected_category_id"]
        selected_category = await Category.get_or_none(id=category_id)
        if selected_category:
            selected_category.name = new_category_name
            await selected_category.save()
        await bot.send_message(
            user_id,
            f"Категорію було перейменовано на - '{new_category_name}'.",
            reply_markup=await main_keyboard(user_id),
        )
        logging.info(
            f"User {message.from_user.id} renamed existing category ({category_id}) - '{new_category_name}'"
        )

    await state.finish()


@dp.callback_query_handler(lambda query: query.data.startswith("delete_category_"))
async def delete_category(query: types.CallbackQuery):
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

    category_id = int(query.data.split("_")[2])
    category = await Category.get_or_none(id=category_id)

    if category:
        await bot.send_message(
            user_id,
            f"Ви впевнені, що бажаєте видалити категорію '{category.name}'?",
            reply_markup=await confirmation_delete_category_keyboard(category_id),
        )
    else:
        await bot.answer_callback_query(query.id, text="Категорію не знайдено.")


@dp.callback_query_handler(
    lambda query: query.data.startswith("confirm_delete_category_")
)
async def confirm_delete_data(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    category_id = int(query.data.split("_")[3])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        category = await Category.get_or_none(id=category_id)

        if category:
            subcategories = await SubCategory.filter(category=category)

            for subcategory in subcategories:
                subcategory_data = await SubCategoryData.filter(subcategory=subcategory)
                for data_entry in subcategory_data:
                    await data_entry.delete()  # Delete all data in selected SubCategory.

                childcategories = await ChildCategory.filter(subcategory=subcategory)
                if childcategories:
                    for childcategory in childcategories:
                        childcategory_data = await ChildCategoryData.filter(
                            childcategory=childcategory
                        )
                        for data_entry in childcategory_data:
                            await data_entry.delete()  # Delete all data entries in selected ChildCategory.
                        await childcategory.delete()  # Delete all CHildCategories as well.

                await subcategory.delete()  # Delete all SubCategories in selected Category.

            await category.delete()  # Delete selected Category.
            await bot.send_message(
                user_id,
                f"Категорію '{category.name}' та всі пов'язані з нею дані та підкатегорії було видалено.",
            )
            logging.info(
                f"User {query.from_user.id} deleted category - '{category.name}'."
            )
        else:
            await bot.send_message(user_id, "Помилка: Категорію не знайдено.")
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )
