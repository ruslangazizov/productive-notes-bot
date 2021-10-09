from typing import List, Tuple

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.main_menu import get_and_save_category, get_category
from handlers.users.start import reset_state_saving_user_id
from keyboards.default import main_menu
from keyboards.inline.callback_data import number_callback
from keyboards.inline.numbers import get_number_buttons
from loader import dp, db
from states.notes import ChangeNote

NUMBER_OF_BUTTONS_IN_INLINE_KEYBOARD = 9


@dp.callback_query_handler(state=ChangeNote.choose_category)
async def send_last_notes(call: types.CallbackQuery, state: FSMContext):
    category = await get_and_save_category(call, state)
    user_tg_id = (await state.get_data()).get("user_tg_id")

    message_text = f"Последние заметки в категории <b>{category}</b>:"
    notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)
    number_of_notes = len(notes_in_category)
    if number_of_notes == 0:
        message_text = f"Нет заметок в категории <b>{category}</b>"
    for index, note in enumerate(notes_in_category[:NUMBER_OF_BUTTONS_IN_INLINE_KEYBOARD]):
        note_text = note[:45]
        if len(note) > 45:
            note_text += "..."
        message_text += f"\n{index + 1}) {note_text}"
    further_button = None
    if number_of_notes > NUMBER_OF_BUTTONS_IN_INLINE_KEYBOARD:
        message_text += f"\n{NUMBER_OF_BUTTONS_IN_INLINE_KEYBOARD + 1}) ..."
        number_of_notes = NUMBER_OF_BUTTONS_IN_INLINE_KEYBOARD
        further_button = "Далее ⏩"

    await state.update_data(last_note_number=number_of_notes)
    await call.message.answer(message_text,
                              reply_markup=get_number_buttons(1, number_of_notes, further_button))
    await ChangeNote.choose_note.set()


@dp.callback_query_handler(number_callback.filter(value="Далее ⏩"), state=ChangeNote.choose_note)
async def show_further(call: types.CallbackQuery, state: FSMContext):
    last_note_number = await get_last_note_number(state)
    category = await get_category(state)
    user_tg_id = (await state.get_data()).get("user_tg_id")

    notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)
    # notes_in_category.reverse()  # чтобы выводить заметки начиная с последних
    number_of_notes = len(notes_in_category)
    new_first_note_number, new_last_note_number = last_note_number + 1, number_of_notes
    if new_last_note_number > last_note_number + NUMBER_OF_BUTTONS_IN_INLINE_KEYBOARD:
        new_last_note_number = last_note_number + NUMBER_OF_BUTTONS_IN_INLINE_KEYBOARD
    message_text = f"Заметки №{new_first_note_number} - №{new_last_note_number} в категории <b>{category}</b>:"
    for index, note in enumerate(notes_in_category[new_first_note_number - 1:new_last_note_number]):
        note_text = note[:45]
        if len(note) > 45:
            note_text += "..."
        message_text += f"\n{index + 1}) {note_text}"
    if len(notes_in_category) > new_last_note_number:
        message_text += f"\n{new_last_note_number + 1}) ..."

    current_number_of_buttons = new_last_note_number - new_first_note_number + 1
    further_button = None
    if number_of_notes > new_last_note_number:
        further_button = "Далее ⏩"

    await state.update_data(last_note_number=new_last_note_number)
    await call.message.answer(message_text, reply_markup=get_number_buttons(new_first_note_number,
                                                                            current_number_of_buttons,
                                                                            further_button))


@dp.callback_query_handler(state=ChangeNote.choose_note)
async def show_note_full(call: types.CallbackQuery, state: FSMContext):
    note_number = await get_and_save_number(call, state)
    category = await get_category(state)
    user_tg_id = (await state.get_data()).get("user_tg_id")

    notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)

    note_text = notes_in_category[note_number - 1]
    message_text = f"<b>Полный текст заметки</b>: (категория - <b>{category}</b>)\n\n" \
                   f"{note_text}\n\n" \
                   f"<b>Введите новый текст заметки</b>"

    await state.update_data(old_note_text=note_text)
    await call.message.answer(message_text)
    await ChangeNote.save_note.set()


@dp.message_handler(state=ChangeNote.save_note)
async def save_changed_note(message: types.Message, state: FSMContext):
    old_note_text = await get_old_note_text(state)
    changed_note_text = message.text
    note_category, note_number = await get_category_and_number(state)
    user_tg_id = message.from_user.id
    await state.update_data(user_tg_id=user_tg_id)

    await db.update_note_text(old_note_text, changed_note_text, user_tg_id, note_category)

    message_text = f"Заметка №{note_number} из категории <b>{note_category}</b> успешно обновлена"
    await message.answer(message_text, reply_markup=main_menu)
    await reset_state_saving_user_id(state)


async def get_and_save_number(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()

    number = int(call.data.split(':')[-1])
    await state.update_data(number=number)

    return number


async def get_last_note_number(state: FSMContext) -> int:
    data = await state.get_data()
    return data.get("last_note_number")


async def get_old_note_text(state: FSMContext) -> int:
    data = await state.get_data()
    return data.get("old_note_text")


async def get_category_and_number(state: FSMContext) -> Tuple[str, str]:
    note_data = await state.get_data()
    note_category = note_data.get("category_name")
    note_number = note_data.get("number")
    return note_category, note_number
