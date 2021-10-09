from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from handlers.users.start import reset_state_saving_user_id
from keyboards.default import back_menu, main_menu
from keyboards.inline.callback_data import category_callback
from keyboards.inline.categories import get_categories_buttons
from keyboards.inline.show_all_button import show_all_button
from loader import dp, db
from states.notes import AddNote, ChangeNote, ShowNote, DeleteNote


@dp.message_handler(Text(equals=["Добавить заметку", "Посмотреть заметки",
                                 "Изменить заметку", "Удалить заметку"]))
async def choose_category(message: types.Message):
    categories_buttons = None
    user_categories_lst: List[str] = await db.get_user_categories(message.from_user.id)
    if message.text in ("Добавить заметку", "Изменить заметку", "Удалить заметку"):
        categories_buttons = get_categories_buttons(categories=user_categories_lst)
    elif message.text == "Посмотреть заметки":
        categories_buttons = get_categories_buttons("Показать все заметки",
                                                    categories=user_categories_lst)
    await message.answer("Выберите категорию", reply_markup=categories_buttons)
    await message.answer("Чтобы вернуться в главное меню, нажмите <b>Главное меню</b>",
                         reply_markup=back_menu)
    if message.text == "Добавить заметку":
        await AddNote.choose_category.set()
    elif message.text == "Посмотреть заметки":
        await ShowNote.choose_category.set()
    elif message.text == "Изменить заметку":
        await ChangeNote.choose_category.set()
    elif message.text == "Удалить заметку":
        await DeleteNote.choose_category.set()


@dp.callback_query_handler(state=AddNote.choose_category)
async def add_note(call: types.CallbackQuery, state: FSMContext):
    category = await get_and_save_category(call, state)

    await call.message.answer(f"Введите новую заметку для категории <b>{category}</b>")
    await AddNote.add_note.set()


@dp.message_handler(state=AddNote.add_note)
async def save_note(message: types.Message, state: FSMContext):
    category = (await state.get_data()).get("category_name")
    note_text = message.text
    user_tg_id = message.from_user.id
    await state.update_data(user_tg_id=user_tg_id)

    await db.add_note(user_tg_id, category, note_text)

    await message.answer(f"Заметка\n<i>{note_text}</i>\nуспешно добавлена "
                         f"в категорию <b>{category}</b>", reply_markup=main_menu)
    await reset_state_saving_user_id(state)


@dp.callback_query_handler(category_callback.filter(category_name="Показать все заметки"),
                           state=ShowNote.choose_category)
async def show_all_notes_in_all_categories_short(call: types.CallbackQuery, state: FSMContext):
    message_text = "<b>Последние заметки:</b>"
    user_tg_id = (await state.get_data()).get("user_tg_id")

    user_categories_lst: List[str] = await db.get_user_categories(user_tg_id)
    show_button = False
    for category in user_categories_lst:
        message_text += f"\n<i>{category}:</i>"
        notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)
        for index, note in enumerate(notes_in_category[-3:]):
            message_text += f"\n{index + 1}) {note}"
        if len(notes_in_category) > 3:
            message_text += "\n4) ..."
            show_button = True

    if show_button:
        await call.message.answer(message_text, reply_markup=show_all_button)
        await ShowNote.show_all_notes_in_all_categories.set()
    else:
        await call.message.answer(message_text)
        # await state.reset_state()


@dp.callback_query_handler(category_callback.filter(category_name="show_all_button"),
                           state=ShowNote.show_all_notes_in_all_categories)
async def show_all_notes_in_all_categories_full(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    message_text = "<b>Все заметки:</b>"
    user_tg_id = (await state.get_data()).get("user_tg_id")

    user_categories_lst: List[str] = await db.get_user_categories(user_tg_id)
    for category in user_categories_lst:
        message_text += f"\n<i>{category}:</i>"
        notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)
        for index, note in enumerate(notes_in_category):
            message_text += f"\n{index + 1}) {note}"

    await call.message.answer(message_text, reply_markup=main_menu)
    await reset_state_saving_user_id(state)


@dp.callback_query_handler(state=ShowNote.choose_category)
async def show_last_notes_in_category(call: types.CallbackQuery, state: FSMContext):
    category = await get_and_save_category(call, state)
    user_tg_id = (await state.get_data()).get("user_tg_id")

    message_text = f"Последние заметки в категории <b>{category}</b>:"
    notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)
    show_button = False
    if len(notes_in_category) == 0:
        message_text = f"Нет заметок в категории <b>{category}</b>"
    else:
        for index, note in enumerate(notes_in_category[-5:]):
            message_text += f"\n{index + 1}) {note}"
        if len(notes_in_category) > 5:
            message_text += "\n6) ..."
            show_button = True

    if show_button:
        await call.message.answer(message_text, reply_markup=show_all_button)
        await ShowNote.show_all_notes_in_one_category.set()
    else:
        await call.message.answer(message_text)


@dp.callback_query_handler(state=ShowNote.show_all_notes_in_one_category)
async def show_all_notes_in_category(call: types.CallbackQuery, state: FSMContext):
    category = (await state.get_data()).get("category_name")
    user_tg_id = (await state.get_data()).get("user_tg_id")

    message_text = f"Все заметки в категории <b>{category}</b>:"
    notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)
    for index, note in enumerate(notes_in_category):
        message_text += f"\n{index + 1}) {note}"

    await call.message.answer(message_text)
    await ShowNote.showed_all_notes_in_one_category.set()


async def get_and_save_category(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()

    category = call.data.split(':')[-1]
    await state.update_data(category_name=category)

    return category


async def get_category(state: FSMContext):
    data = await state.get_data()
    return data.get("category_name")
