from typing import List, Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from handlers.users.main_menu import get_and_save_category, get_category
from handlers.users.start import reset_state_saving_user_id
from keyboards.default import back_menu, main_menu
from keyboards.inline.callback_data import confirmation_callback
from keyboards.inline.categories import get_categories_buttons
from keyboards.inline.categories_actions import categories_actions, confirmation_buttons
from loader import dp, db
from states.categories import DeleteCategory, AddCategory


@dp.message_handler(Text(equals="Категории"))
async def show_all_categories(message: Union[types.Message, CallbackQuery], state: FSMContext, show_info=True):
    message_text = "Ваши категории:"
    if isinstance(message, types.Message):
        user_tg_id = message.from_user.id
        await state.update_data(user_tg_id=user_tg_id)
    else:
        user_tg_id = (await state.get_data()).get("user_tg_id")

    user_categories_lst: List[str] = await db.get_user_categories(user_tg_id)
    for index, category in enumerate(user_categories_lst):
        notes_in_category: List[str] = await db.get_user_notes_in_category(user_tg_id, category)
        count_of_notes_in_category = len(notes_in_category)
        message_text += f"\n{index + 1}. <b>{category}</b> (кол-во заметок: {count_of_notes_in_category})"

    if isinstance(message, CallbackQuery):
        message = message.message
    if show_info:
        await message.answer("Чтобы вернуться в главное меню, нажмите <b>Главное меню</b>",
                             reply_markup=back_menu)
    await message.answer(message_text, reply_markup=categories_actions)


@dp.callback_query_handler(confirmation_callback.filter(action_name="delete"))
async def choose_category_to_delete(call: types.CallbackQuery, state: FSMContext):
    message_text = "Выберите категорию, которую хотите удалить:"
    user_tg_id = (await state.get_data()).get("user_tg_id")

    user_categories_lst: List[str] = await db.get_user_categories(user_tg_id)

    await call.message.answer(message_text,
                              reply_markup=get_categories_buttons(categories=user_categories_lst))
    await DeleteCategory.choose_category.set()


@dp.callback_query_handler(state=DeleteCategory.choose_category)
async def delete_category_confirmation(call: types.CallbackQuery, state: FSMContext):
    category = await get_and_save_category(call, state)
    message_text = f"Вы уверены, что хотите удалить категорию <b>{category}</b>?"

    await call.message.answer(message_text, reply_markup=confirmation_buttons)
    await DeleteCategory.delete_confirmation.set()


@dp.callback_query_handler(confirmation_callback.filter(action_name="yes"),
                           state=DeleteCategory.delete_confirmation)
async def delete_category(call: types.CallbackQuery, state: FSMContext):
    category = await get_category(state)
    user_tg_id = (await state.get_data()).get("user_tg_id")

    await db.delete_user_category(user_tg_id, category)

    await call.message.answer(f"Категория <b>{category}</b> успешно удалена", reply_markup=main_menu)
    await reset_state_saving_user_id(state)


@dp.callback_query_handler(confirmation_callback.filter(action_name="no"),
                           state=DeleteCategory.delete_confirmation)
async def deny_delete_category(call: types.CallbackQuery, state: FSMContext):
    await reset_state_saving_user_id(state)
    await show_all_categories(call, state, False)


@dp.callback_query_handler(confirmation_callback.filter(action_name="add"))
async def add_category(call: types.CallbackQuery):
    message_text = "Введите название категории, которую вы хотите добавить"
    await call.message.answer(message_text)
    await AddCategory.write_new_category_name.set()


@dp.message_handler(state=AddCategory.write_new_category_name)
async def category_added(message: types.Message, state: FSMContext):
    new_category_name = message.text
    user_tg_id = message.from_user.id
    await state.update_data(user_tg_id=user_tg_id)

    if await db.add_user_category(user_tg_id, new_category_name):
        await message.answer(f"Категория {new_category_name} успешно создана")
    else:
        await message.answer(f"Категория {new_category_name} уже создана")

    await reset_state_saving_user_id(state)
    await show_all_categories(message, state, False)
