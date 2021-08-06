from aiogram.dispatcher.filters.state import StatesGroup, State


class DeleteCategory(StatesGroup):
    choose_category = State()
    delete_confirmation = State()


class AddCategory(StatesGroup):
    write_new_category_name = State()
