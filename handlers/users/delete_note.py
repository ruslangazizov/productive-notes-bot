from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.change_note import get_and_save_number
from handlers.users.main_menu import get_and_save_category, get_category
from handlers.users.start import reset_state_saving_user_id
from keyboards.default import main_menu
from keyboards.inline.callback_data import confirmation_callback
from keyboards.inline.categories_actions import confirmation_buttons
from keyboards.inline.numbers import get_number_buttons
from loader import dp, db

from states.notes import DeleteNote


@dp.callback_query_handler(state=DeleteNote.choose_category)
async def choose_note(call: types.CallbackQuery, state: FSMContext, category: str = None):
    if not category:
        category = await get_and_save_category(call, state, send_msg_with_category=True)
    else:
        await state.update_data(category_name=category)
    user_tg_id = (await state.get_data()).get("user_tg_id")
    message_text = "Выберите заметку:"

    notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)
    number_of_notes = len(notes_in_category)
    for index, note in enumerate(notes_in_category):
        note_text = note[:45]
        if len(note) > 45:
            note_text += "..."
        message_text += f"\n{index + 1}) {note_text}"

    await call.message.answer(message_text,
                              reply_markup=get_number_buttons(1, number_of_notes))
    await DeleteNote.choose_note.set()


@dp.callback_query_handler(state=DeleteNote.choose_note)
async def delete_note_confirmation(call: types.CallbackQuery, state: FSMContext):
    category = await get_category(state)
    note_number = await get_and_save_number(call, state)
    user_tg_id = (await state.get_data()).get("user_tg_id")
    note_text = (await db.get_user_notes_in_category(user_tg_id, category))[note_number - 1]
    await state.update_data(note_text=note_text)

    message_text = f"<b>Полный текст заметки</b>:\n\n" \
                   f"{note_text}\n\n"\
                   f"Вы уверены, что хотите удалить эту заметку?"

    await call.message.answer(message_text, reply_markup=confirmation_buttons)
    await DeleteNote.delete_confirmation.set()


@dp.callback_query_handler(confirmation_callback.filter(action_name="yes"),
                           state=DeleteNote.delete_confirmation)
async def delete_note(call: types.CallbackQuery, state: FSMContext):
    category = await get_category(state)
    state_data = await state.get_data()
    note_text = state_data.get("note_text")
    user_tg_id = state_data.get("user_tg_id")

    await db.delete_note(user_tg_id, category, note_text)

    short_note_text = note_text[:15] + "..." if len(note_text) > 15 else note_text
    await call.message.answer(f"Заметка <b>{short_note_text}</b> успешно удалена",
                              reply_markup=main_menu)
    await reset_state_saving_user_id(state)


@dp.callback_query_handler(confirmation_callback.filter(action_name="no"),
                           state=DeleteNote.delete_confirmation)
async def deny_delete_note(call: types.CallbackQuery, state: FSMContext):
    category = await get_category(state)
    await reset_state_saving_user_id(state)

    await choose_note(call, state, category)
