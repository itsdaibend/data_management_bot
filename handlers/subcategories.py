from aiogram import types
from aiogram.dispatcher import FSMContext

from forms import DataEntryForm, EditSubcategoryForm
from keyboards import (
    confirmation_data_delete_keyboard,
    confirmation_delete_subcategory_keyboard,
    subcategories_data_delete_keyboard,
    subcategories_data_keyboard,
    subcategories_keyboard,
    subcategories_user_data_keyboard,
    view_subcategory_keyboard,
)
from misc import *
from bot_logging import *
from models import (
    Category,
    ChildCategory,
    ChildCategoryData,
    SubCategory,
    SubCategoryData,
)


@dp.message_handler(
    content_types=types.ContentTypes.ANY, state=DataEntryForm.WaitingForFile
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
        subcategory_id = data["subcategory_id"]

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

        new_data_entry = await SubCategoryData.create(
            subcategory_id=subcategory_id,
            file_id=file_id,
            file_type=file_type,
            created_by=user_id,
        )

        keyboard = await subcategories_data_keyboard(subcategory_id, "➕ Додати ще дані")
        await bot.send_message(
            user_id, f"Додано новий запис: Тип - {file_type}.", reply_markup=keyboard
        )
        logging.info(f"User {message.from_user.id} added data, type - '{file_type}' .")

    await state.finish()


@dp.callback_query_handler(lambda query: query.data.startswith("delete_data_"))
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

    data_entry_id = int(query.data.split("_")[2])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        keyboard = await confirmation_data_delete_keyboard(data_entry_id)

        await bot.send_message(
            user_id,
            "Чи дійсно ви бажаєте видалити цей файл?",
            reply_markup=keyboard,
        )
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.callback_query_handler(lambda query: query.data.startswith("confirm_delete_data_"))
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

    data_entry_id = int(query.data.split("_")[3])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        data_entry = await SubCategoryData.get_or_none(id=data_entry_id)

        if data_entry:
            await data_entry.delete()
            await bot.send_message(user_id, "Дані було видалено.")
            logging.info(f"User {query.from_user.id} deleted data entry.")
        else:
            await bot.send_message(user_id, "Помилка: Дані не знайдено.")
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.callback_query_handler(
    lambda query: query.data.startswith("edit_subcategory_name_")
)
async def edit_existing_subcategory_name(query: types.CallbackQuery, state: FSMContext):
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

    subcategory_id = int(query.data.split("_")[3])

    await bot.answer_callback_query(query.id)  # To close the pop-up notification

    await bot.send_message(user_id, "Введіть нову назву для цієї підкатегорії:")
    await EditSubcategoryForm.WaitingForNewSubcategoryName.set()
    await state.update_data(selected_subcategory_id=subcategory_id)


@dp.message_handler(state=EditSubcategoryForm.WaitingForNewSubcategoryName)
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

    new_subcategory_name = message.text
    if not new_subcategory_name:
        await bot.send_message(user_id, "Ви не ввели назву нової підкатегорії.")
    else:
        subcategory_id = (await state.get_data())["selected_subcategory_id"]
        keyboard = await subcategories_data_keyboard(subcategory_id)
        selected_subcategory = await SubCategory.get_or_none(id=subcategory_id)
        if selected_subcategory:
            selected_subcategory.name = new_subcategory_name
            await selected_subcategory.save()
        await bot.send_message(
            user_id,
            f"Підкатегорію було перейменовано на - '{new_subcategory_name}'.",
            reply_markup=keyboard,
        )
        logging.info(
            f"User {message.from_user.id} renamed existing subcategory ({subcategory_id}) - '{new_subcategory_name}'"
        )

    await state.finish()


@dp.callback_query_handler(lambda query: query.data.startswith("delete_subcategory_"))
async def delete_subcategory(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """Выход из хендлера для незарегистрированных пользователей"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    subcategory_id = int(query.data.split("_")[2])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        subcategory = await SubCategory.get_or_none(id=subcategory_id)

        if subcategory:
            await bot.send_message(
                user_id,
                f"Ви впевнені, що бажаєте видалити підкатегорію '{subcategory.name}'?",
                reply_markup=await confirmation_delete_subcategory_keyboard(
                    subcategory.id
                ),
            )
        else:
            await bot.answer_callback_query(query.id, text="Підатегорію не знайдено.")

    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.callback_query_handler(
    lambda query: query.data.startswith("confirm_delete_subcategory_")
)
async def confirm_delete_subcategory(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    subcategory_id = int(query.data.split("_")[3])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        subcategory = await SubCategory.get_or_none(id=subcategory_id)

        if subcategory:
            parent_category = await subcategory.category
            selected_category_id = parent_category.id
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

            await subcategory.delete()  # Delete SubCategory.

            subcategories = await SubCategory.filter(category_id=selected_category_id)
            message_text = parent_category.name

            previous_category = (
                await Category.filter(id__lt=selected_category_id)
                .order_by("-id")
                .first()
            )
            next_category = (
                await Category.filter(id__gt=selected_category_id)
                .order_by("id")
                .first()
            )

            keyboard = await subcategories_keyboard(
                subcategories,
                user_id,
                selected_category_id,
                previous_category.id if previous_category else None,
                next_category.id if next_category else None,
            )

            await bot.send_message(
                user_id,
                f"Підкатегорію '{subcategory.name}' та всі пов'язані з нею дані та підкатегорії було видалено.",
            )
            logging.info(
                f"User {query.from_user.id} deleted subcategory - '{subcategory.name}'."
            )
            await bot.send_message(
                query.from_user.id, message_text, reply_markup=keyboard
            )
        else:
            await bot.send_message(user_id, "Помилка: Підатегорію не знайдено.")
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.callback_query_handler(lambda query: query.data.startswith("add_subcategory_"))
async def request_subcategory_name(query: types.CallbackQuery, state: FSMContext):
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
    category_id = int(query.data.split("_")[2])

    if user_is_superuser(user_id):
        await bot.send_message(user_id, "Введіть назву нової підкатегорії:")
        # Save the information about the selected category and wait for the name of the subcategory to be entered
        await state.set_state("waiting_for_subcategory_name")
        await state.update_data(selected_category_id=category_id)
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.message_handler(state="waiting_for_subcategory_name")
async def add_subcategory_name(message: types.Message, state: FSMContext):
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
    selected_category_id = (await state.get_data())["selected_category_id"]

    new_subcategory_name = message.text
    new_subcategory = await SubCategory.create(
        name=new_subcategory_name, category_id=selected_category_id, created_by=user_id
    )

    parent_category = await Category.get(id=selected_category_id)
    subcategories = await SubCategory.filter(category_id=selected_category_id)

    message_text = parent_category.name

    previous_category = (
        await Category.filter(id__lt=selected_category_id).order_by("-id").first()
    )
    next_category = (
        await Category.filter(id__gt=selected_category_id).order_by("id").first()
    )

    keyboard = await subcategories_keyboard(
        subcategories,
        message.from_user.id,
        selected_category_id,
        previous_category.id if previous_category else None,
        next_category.id if next_category else None,
    )

    await message.answer(f"Створено нову підкатегорію '{new_subcategory.name}'.")
    await bot.send_message(message.from_user.id, message_text, reply_markup=keyboard)
    logging.info(
        f"User {message.from_user.id} created a new subcategory - '{new_subcategory.name}'."
    )
    await state.reset_state()


@dp.callback_query_handler(lambda query: query.data.startswith("view_subcategory_"))
async def view_subcategory_data(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    subcategory_id = int(query.data.split("_")[2])
    subcategory = await SubCategory.get_or_none(id=subcategory_id)

    user_id = query.from_user.id
    if user_is_superuser(user_id):
        keyboard = await subcategories_data_keyboard(subcategory_id)
    else:
        keyboard = await subcategories_user_data_keyboard(subcategory_id)

    if subcategory:
        subcategory_data = await SubCategoryData.filter(subcategory=subcategory)

        if subcategory_data:
            sent_message = await bot.send_message(
                query.from_user.id,
                subcategory.name,
                reply_markup=keyboard,
            )
            for data_entry in subcategory_data:
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
                    deletion_keyboard = await subcategories_data_delete_keyboard(
                        data_entry
                    )
                    await bot.edit_message_reply_markup(
                        chat_id=sent_message.chat.id,
                        message_id=sent_message.message_id,
                        reply_markup=deletion_keyboard,
                    )

            await bot.send_message(
                query.from_user.id,
                "Ви переглянули всі дані з цієї підкатегорії. Що бажаєте зробити далі?",
                reply_markup=await view_subcategory_keyboard(subcategory),
            )
        else:
            if user_is_superuser(user_id):
                await bot.send_message(
                    query.from_user.id,
                    subcategory.name,
                    reply_markup=keyboard,
                )
            else:
                await bot.send_message(
                    query.from_user.id,
                    subcategory.name,
                )
    else:
        await bot.answer_callback_query(query.id, text="Підкатегорія не знайдена.")


@dp.callback_query_handler(lambda query: query.data.startswith("add_data_"))
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

    subcategory_id = int(query.data.split("_")[2])
    user_id = query.from_user.id

    await DataEntryForm.WaitingForFile.set()
    await state.update_data(subcategory_id=subcategory_id)

    await bot.send_message(user_id, "Будь ласка, надішліть файл або введіть текст:")
