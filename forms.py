from aiogram.dispatcher.filters.state import State, StatesGroup


class DataEntryForm(StatesGroup):
    WaitingForFileType = State()
    WaitingForFile = State()


class ChildCategoryDataEntryForm(StatesGroup):
    WaitingForFileType = State()
    WaitingForFile = State()


class CategoryDataEntryForm(StatesGroup):
    WaitingForFileType = State()
    WaitingForFile = State()


class CreateCategoryForm(StatesGroup):
    WaitingForNewCategoryName = State()


class EditCategoryForm(StatesGroup):
    WaitingForNewCategoryName = State()


class EditChildCategoryForm(StatesGroup):
    WaitingForNewChildCategoryName = State()


class EditSubcategoryForm(StatesGroup):
    WaitingForNewSubcategoryName = State()


class EditDataEntryForm(StatesGroup):
    WaitingForNewDataEntryText = State()
