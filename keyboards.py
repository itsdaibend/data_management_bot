from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from models import Category, ChildCategory, SubCategory
from config import SUPERUSER_IDS


async def main_keyboard(user_id):
    categories = await Category.all().order_by("id")
    keyboard = InlineKeyboardMarkup()
    for category in categories:
        keyboard.add(
            InlineKeyboardButton(
                text=category.name, callback_data=f"category_{category.id}"
            )
        )

    if str(user_id) in SUPERUSER_IDS:
        keyboard.add(
            InlineKeyboardButton(
                text="➕ Додати нову категорію", callback_data="new_category"
            )
        )

    return keyboard


async def subcategories_keyboard(
    subcategories, user_id, category_id, previous_category_id, next_category_id
):
    keyboard = InlineKeyboardMarkup()
    for subcategory in subcategories:
        keyboard.add(
            InlineKeyboardButton(
                text=subcategory.name,
                callback_data=f"view_subcategory_{subcategory.id}",
            )
        )

    if str(user_id) in SUPERUSER_IDS:
        keyboard.add(
            InlineKeyboardButton(
                text="➕ Додати нову підкатегорію",
                callback_data=f"add_subcategory_{category_id}",
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="✍️ Редагувати назву цієї категорії",
                callback_data=f"edit_category_name_{category_id}",
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="❗️ Видалити цю категорію",
                callback_data=f"delete_category_{category_id}",
            )
        )

    if previous_category_id and not next_category_id:
        previous_button = InlineKeyboardButton(
            text="⬅️ Попередня категорія",
            callback_data=f"category_{previous_category_id}",
        )
        keyboard.add(previous_button)
    if next_category_id and not previous_category_id:
        next_button = InlineKeyboardButton(
            text="Наступна категорія ➡️", callback_data=f"category_{next_category_id}"
        )
        keyboard.add(next_button)
    if previous_category_id and next_category_id:
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Категорія", callback_data=f"category_{previous_category_id}"
            ),
            InlineKeyboardButton(
                text="Категорія ➡️", callback_data=f"category_{next_category_id}"
            ),
        )

    keyboard.add(
        InlineKeyboardButton(text="↩️ До основного меню", callback_data="main_menu")
    )

    return keyboard


async def childcategories_keyboard(childcategories, user_id, selected_subcategory_id):
    keyboard = InlineKeyboardMarkup()
    for childcategory in childcategories:
        keyboard.add(
            InlineKeyboardButton(
                text=childcategory.name,
                callback_data=f"view_childcategory_{childcategory.id}",
            )
        )

    if str(user_id) in SUPERUSER_IDS:
        keyboard.add(
            InlineKeyboardButton(
                text="➕ Додати новий підрозділ",
                callback_data=f"add_childcategory_{selected_subcategory_id}",
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="✍️ Редагувати назву цього підрозділу",
                callback_data=f"edit_childcategory_name_{selected_subcategory_id}",
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="❗️ Видалити цей підрозділ",
                callback_data=f"delete_childcategory_{selected_subcategory_id}",
            )
        )

    return keyboard


async def childcategories_data_add_keyboard(childcategory_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="➕ Додати дані",
            callback_data=f"add_child_category_data_{childcategory_id}",
        )
    )

    return keyboard


async def categories_data_add_keyboard(category_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="➕ Додати дані", callback_data=f"add_category_data_{category_id}"
        )
    )

    return keyboard


async def subcategories_data_keyboard(subcategory_id, text="➕ Додати дані"):
    keyboard = InlineKeyboardMarkup()
    subcategory = await SubCategory.get(id=subcategory_id)
    childcategories = await ChildCategory.filter(subcategory=subcategory)
    for category in childcategories:
        keyboard.add(
            InlineKeyboardButton(
                text=category.name, callback_data=f"view_childcategory_{category.id}"
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text="➕ Додати новий підрозділ",
            callback_data=f"add_childcategory_{subcategory_id}",
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Показати всі дані", callback_data=f"view_subcategory_{subcategory_id}"
        )
    )
    keyboard.add(
        InlineKeyboardButton(text=text, callback_data=f"add_data_{subcategory_id}")
    )
    keyboard.add(
        InlineKeyboardButton(
            text="✍️ Редагувати назву цієї підкатегорії",
            callback_data=f"edit_subcategory_name_{subcategory_id}",
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="❗️ Видалити цю підкатегорію",
            callback_data=f"delete_subcategory_{subcategory_id}",
        )
    )

    return keyboard


async def subcategories_user_data_keyboard(subcategory_id):
    keyboard = InlineKeyboardMarkup()
    subcategory = await SubCategory.get(id=subcategory_id)
    childcategories = await ChildCategory.filter(subcategory=subcategory)
    for category in childcategories:
        keyboard.add(
            InlineKeyboardButton(
                text=category.name, callback_data=f"view_childcategory_{category.id}"
            )
        )

    return keyboard


async def childcategories_data_keyboard(childcategory_id, text="➕ Додати дані"):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="Показати всі дані",
            callback_data=f"view_childcategory_{childcategory_id}",
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=text, callback_data=f"add_child_category_data_{childcategory_id}"
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="✍️ Редагувати назву цього підрозділу",
            callback_data=f"edit_childcategory_name_{childcategory_id}",
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="❗️ Видалити цей підрозділ",
            callback_data=f"delete_childcategory_{childcategory_id}",
        )
    )

    return keyboard


async def childcategories_data_delete_keyboard(data_entry):
    keyboard = InlineKeyboardMarkup()

    if data_entry.file_type == "text":
        keyboard.add(
            InlineKeyboardButton(
                text="✍️ Редагувати ці дані",
                callback_data=f"edit_data_entry_childcategory_{data_entry.id}",
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text="❗️ Видалити ці дані",
            callback_data=f"delete_child_category_data_{data_entry.id}",
        )
    )

    return keyboard


async def subcategories_data_delete_keyboard(data_entry):
    keyboard = InlineKeyboardMarkup()

    if data_entry.file_type == "text":
        keyboard.add(
            InlineKeyboardButton(
                text="✍️ Редагувати ці дані",
                callback_data=f"edit_data_entry_subcategory_{data_entry.id}",
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text="❗️ Видалити ці дані", callback_data=f"delete_data_{data_entry.id}"
        )
    )

    return keyboard


async def categories_data_delete_keyboard(data_entry):
    keyboard = InlineKeyboardMarkup()

    if data_entry.file_type == "text":
        keyboard.add(
            InlineKeyboardButton(
                text="✍️ Редагувати ці дані",
                callback_data=f"edit_data_entry_category_{data_entry.id}",
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text="❗️ Видалити ці дані",
            callback_data=f"categories_delete_data_{data_entry.id}",
        )
    )

    return keyboard


async def confirmation_category_data_delete_keyboard(data_entry_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text="❗️ Так", callback_data=f"confirm_category_delete_data_{data_entry_id}"
        )
    )
    keyboard.row(InlineKeyboardButton(text="Ні", callback_data="cancel_delete_data"))

    return keyboard


async def confirmation_child_category_data_delete_keyboard(data_entry_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text="❗️ Так",
            callback_data=f"confirm_child_category_delete_data_{data_entry_id}",
        )
    )
    keyboard.row(InlineKeyboardButton(text="Ні", callback_data="cancel_delete_data"))

    return keyboard


async def confirmation_data_delete_keyboard(data_entry_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text="❗️ Так", callback_data=f"confirm_delete_data_{data_entry_id}"
        )
    )
    keyboard.row(InlineKeyboardButton(text="Ні", callback_data="cancel_delete_data"))

    return keyboard


async def confirmation_delete_category_keyboard(category_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text="❗️ Так", callback_data=f"confirm_delete_category_{category_id}"
        )
    )
    keyboard.row(
        InlineKeyboardButton(text="Ні", callback_data="cancel_delete_category")
    )

    return keyboard


async def confirmation_delete_subcategory_keyboard(subcategory_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text="❗️ Так", callback_data=f"confirm_delete_subcategory_{subcategory_id}"
        )
    )
    keyboard.row(
        InlineKeyboardButton(text="Ні", callback_data="cancel_delete_subcategory")
    )

    return keyboard


async def confirmation_delete_childcategory_keyboard(subcategory_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text="❗️ Так",
            callback_data=f"confirm_delete_childcategory_{subcategory_id}",
        )
    )
    keyboard.row(
        InlineKeyboardButton(text="Ні", callback_data="cancel_delete_subcategory")
    )

    return keyboard


async def get_next_subcategory_or_category(subcategory_id):
    subcategory = await SubCategory.get_or_none(id=subcategory_id)
    if subcategory:
        # Find the next subcategory in the same category
        next_subcategory = (
            await SubCategory.filter(
                category_id=subcategory.category_id, id__gt=subcategory.id
            )
            .order_by("id")
            .first()
        )

        if next_subcategory:
            return next_subcategory  # Return the next subcategory

        # If there is no next subcategory, continue searching for the next category with subcategories
        category = (
            await Category.filter(id__gt=subcategory.category_id).order_by("id").first()
        )
        while category:
            first_subcategory = (
                await SubCategory.filter(category_id=category.id).order_by("id").first()
            )
            if first_subcategory:
                return first_subcategory  # Return the first subcategory in the new category
            # If no subcategory found in the current category, continue to the next category
            category = await Category.filter(id__gt=category.id).order_by("id").first()

    return None  # If the next subcategory or category is not found, return None


async def view_subcategory_keyboard(subcategory):
    subcategory_id = subcategory.id
    category_id = subcategory.category_id
    next_subcategory = await get_next_subcategory_or_category(subcategory_id)
    keyboard = InlineKeyboardMarkup()
    if next_subcategory:
        keyboard.add(
            InlineKeyboardButton(
                text="Наступна підкатегорія",
                callback_data=f"view_subcategory_{str(next_subcategory.id)}",
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text="Меню розділу", callback_data=f"category_{category_id}"
        )
    )
    keyboard.add(
        InlineKeyboardButton(text="↩️ До основного меню", callback_data="main_menu")
    )

    return keyboard


async def view_childcategory_keyboard(childcategory):
    parent_subcategory_id = childcategory.subcategory_id
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="Меню розділу",
            callback_data=f"view_subcategory_{str(parent_subcategory_id)}",
        )
    )
    keyboard.add(
        InlineKeyboardButton(text="↩️ До основного меню", callback_data="main_menu")
    )

    return keyboard
