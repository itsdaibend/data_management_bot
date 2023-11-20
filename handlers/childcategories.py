from aiogram import types
from aiogram.dispatcher import FSMContext

from forms import ChildCategoryDataEntryForm, EditChildCategoryForm
from keyboards import (
    childcategories_data_add_keyboard,
    childcategories_data_delete_keyboard,
    childcategories_data_keyboard,
    confirmation_child_category_data_delete_keyboard,
    confirmation_delete_childcategory_keyboard,
    main_keyboard,
    subcategories_data_keyboard,
    view_childcategory_keyboard,
    view_subcategory_keyboard,
)
from misc import *
from bot_logging import *
from models import ChildCategory, ChildCategoryData, SubCategory


@dp.callback_query_handler(
    lambda query: query.data.startswith("delete_child_category_data_")
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

    data_entry_id = int(query.data.split("_")[4])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        keyboard = await confirmation_child_category_data_delete_keyboard(data_entry_id)

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
    lambda query: query.data.startswith("confirm_child_category_delete_data_")
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

    data_entry_id = int(query.data.split("_")[5])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        data_entry = await ChildCategoryData.get_or_none(id=data_entry_id)

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
    lambda query: query.data.startswith("edit_childcategory_name_")
)
async def edit_existing_childcategory_name(
    query: types.CallbackQuery, state: FSMContext
):
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

    childcategory_id = int(query.data.split("_")[3])

    await bot.answer_callback_query(query.id)  # To close the pop-up notification

    await bot.send_message(user_id, "Введіть нову назву для цього підрозділу:")
    await EditChildCategoryForm.WaitingForNewChildCategoryName.set()
    await state.update_data(selected_childcategory_id=childcategory_id)


@dp.message_handler(state=EditChildCategoryForm.WaitingForNewChildCategoryName)
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
        category_id = (await state.get_data())["selected_childcategory_id"]
        selected_childcategory = await ChildCategory.get_or_none(id=category_id)
        if selected_childcategory:
            selected_childcategory.name = new_category_name
            await selected_childcategory.save()
        await bot.send_message(
            user_id,
            f"Підрозділ було перейменовано на - '{new_category_name}'.",
            reply_markup=await main_keyboard(user_id),
        )
        logging.info(
            f"User {message.from_user.id} renamed existing ChildCategory ({category_id}) - '{new_category_name}'"
        )

    await state.finish()


@dp.callback_query_handler(lambda query: query.data.startswith("delete_childcategory_"))
async def delete_childcategory(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """Выход из хендлера для незарегистрированных пользователей"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    childcategory_id = int(query.data.split("_")[2])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        childcategory = await ChildCategory.get_or_none(id=childcategory_id)

        if childcategory:
            await bot.send_message(
                user_id,
                f"Ви впевнені, що бажаєте видалити підрозділ '{childcategory.name}'?",
                reply_markup=await confirmation_delete_childcategory_keyboard(
                    childcategory.id
                ),
            )
        else:
            await bot.answer_callback_query(query.id, text="Підатегорію не знайдено.")

    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.callback_query_handler(
    lambda query: query.data.startswith("confirm_delete_childcategory_")
)
async def confirm_delete_childcategory(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    childcategory_id = int(query.data.split("_")[3])
    user_id = query.from_user.id

    if user_is_superuser(user_id):
        childcategory = await ChildCategory.get_or_none(id=childcategory_id)

        if childcategory:
            parent_category = await childcategory.subcategory
            selected_subcategory_id = parent_category.id
            childcategory_data = await ChildCategoryData.filter(
                childcategory=childcategory
            )
            for data_entry in childcategory_data:
                await data_entry.delete()  # Delete all data in selected SubCategory.

            await childcategory.delete()  # Delete SubCategory.

            subcategories = await SubCategory.filter(id=selected_subcategory_id)
            message_text = parent_category.name

            keyboard = await view_subcategory_keyboard(parent_category)

            await bot.send_message(
                user_id,
                f"Підрозділ '{childcategory.name}' та всі пов'язані з ним дані було видалено.",
            )
            logging.info(
                f"User {query.from_user.id} deleted childcategory - '{childcategory.name}'."
            )
            await bot.send_message(
                query.from_user.id, message_text, reply_markup=keyboard
            )
        else:
            await bot.send_message(user_id, "Помилка: Підкатегорію не знайдено.")
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.callback_query_handler(lambda query: query.data.startswith("add_childcategory_"))
async def request_childcategory_name(query: types.CallbackQuery, state: FSMContext):
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
    subcategory_id = int(query.data.split("_")[2])

    if user_is_superuser(user_id):
        await bot.send_message(user_id, "Введіть назву нового підрозділу:")
        # Save the information about the selected category and wait for the name of the subcategory to be entered
        await state.set_state("waiting_for_childcategory_name")
        await state.update_data(selected_subcategory_id=subcategory_id)
    else:
        await bot.answer_callback_query(
            query.id, text="⛔️ У вас немає дозволу на цю дію."
        )


@dp.message_handler(state="waiting_for_childcategory_name")
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
    selected_subcategory_id = (await state.get_data())["selected_subcategory_id"]

    new_childcategory_name = message.text
    new_childcategory = await ChildCategory.create(
        name=new_childcategory_name,
        subcategory_id=selected_subcategory_id,
        created_by=user_id,
    )

    parent_subcategory = await SubCategory.get(id=selected_subcategory_id)
    childcategories = await ChildCategory.filter(subcategory_id=selected_subcategory_id)

    message_text = parent_subcategory.name

    keyboard = await subcategories_data_keyboard(parent_subcategory.id)

    await message.answer(f"Створено новий підрозділ '{new_childcategory.name}'.")
    await bot.send_message(message.from_user.id, message_text, reply_markup=keyboard)
    logging.info(
        f"User {message.from_user.id} created a new childcategory - '{new_childcategory.name}'."
    )
    await state.reset_state()


@dp.callback_query_handler(lambda query: query.data.startswith("view_childcategory_"))
async def view_childcategory_data(query: types.CallbackQuery):
    if not user_is_whitelisted(query.from_user.id):
        """exit handler for unregistered users"""
        logging.warning(
            f"User {query.from_user.id} tried to start the bot, but is not in WHITE_LIST."
        )
        await query.answer(
            "Вибачте, вам заборонено використовувати цього бота. Будь ласка, зв'яжіться з адміністратором.."
        )
        return

    childcategory_id = int(query.data.split("_")[2])
    childcategory = await ChildCategory.get_or_none(id=childcategory_id)

    user_id = query.from_user.id
    if user_is_superuser(user_id):
        keyboard = await childcategories_data_keyboard(childcategory_id)

    if childcategory:
        childcategory_data = await ChildCategoryData.filter(childcategory=childcategory)

        if childcategory_data:
            sent_message = await bot.send_message(
                query.from_user.id, f"Обраний підрозділ - {childcategory.name}"
            )
            if user_is_superuser(user_id):
                await bot.edit_message_reply_markup(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    reply_markup=keyboard,
                )
            for data_entry in childcategory_data:
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
                    deletion_keyboard = await childcategories_data_delete_keyboard(
                        data_entry
                    )
                    await bot.edit_message_reply_markup(
                        chat_id=sent_message.chat.id,
                        message_id=sent_message.message_id,
                        reply_markup=deletion_keyboard,
                    )

            await bot.send_message(
                query.from_user.id,
                "Ви переглянули всі дані з цього підрозділу. Що бажаєте зробити далі?",
                reply_markup=await view_childcategory_keyboard(childcategory),
            )
        else:
            if user_is_superuser(user_id):
                await bot.send_message(
                    query.from_user.id,
                    childcategory.name,
                    reply_markup=keyboard,
                )
            else:
                await bot.send_message(
                    query.from_user.id,
                    childcategory.name,
                )
    else:
        await bot.answer_callback_query(query.id, text="Підрозділ не знайдено.")


@dp.callback_query_handler(
    lambda query: query.data.startswith("add_child_category_data_")
)
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

    childcategory_id = int(query.data.split("_")[4])
    user_id = query.from_user.id

    await ChildCategoryDataEntryForm.WaitingForFile.set()
    await state.update_data(childcategory_id=childcategory_id)

    await bot.send_message(user_id, "Будь ласка, надішліть файл або введіть текст:")


@dp.message_handler(
    content_types=types.ContentTypes.ANY,
    state=ChildCategoryDataEntryForm.WaitingForFile,
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
        childcategory_id = data["childcategory_id"]

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

        new_data_entry = await ChildCategoryData.create(
            childcategory_id=childcategory_id,
            file_id=file_id,
            file_type=file_type,
            created_by=user_id,
        )

        keyboard = await childcategories_data_add_keyboard(childcategory_id)
        await bot.send_message(
            user_id, f"Додано новий запис: Тип - {file_type}.", reply_markup=keyboard
        )
        logging.info(
            f"User {message.from_user.id} added ChildCategory data, type - '{file_type}' ."
        )

    await state.finish()
