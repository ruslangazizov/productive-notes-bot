from aiogram.dispatcher.filters.state import StatesGroup, State


class AddNote(StatesGroup):
    choose_category = State()
    add_note = State()


class ChangeNote(StatesGroup):
    choose_category = State()
    choose_note = State()
    save_note = State()


class ShowNote(StatesGroup):
    choose_category = State()
    go_to_next_page = State()
    show_all_notes_in_all_categories = State()
    show_all_notes_in_one_category = State()
    showed_all_notes_in_one_category = State()


class DeleteNote(StatesGroup):
    choose_category = State()
    choose_note = State()
    delete_confirmation = State()
