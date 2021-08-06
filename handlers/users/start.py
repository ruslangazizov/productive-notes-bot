from asyncpg import exceptions

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from handlers.users.help import show_bot_help
from keyboards.default import main_menu
from loader import dp, db
from utils.notify_admins import on_user_press_start_notify


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    try:
        await db.add_user(message.from_user.full_name, message.from_user.username, message.from_user.id)
    except exceptions.UniqueViolationError:
        pass
    # await state.set_state("start")
    await state.update_data(user_tg_id=message.from_user.id)

    await message.answer(f"Привет, {message.from_user.full_name}!")
    await show_bot_help(message)
    await message.answer("Выберите действие из меню ниже", reply_markup=main_menu)

    await on_user_press_start_notify(dp, message.from_user.username)


async def reset_state_saving_user_id(state: FSMContext):
    user_tg_id = (await state.get_data()).get("user_tg_id")
    await state.reset_state()
    await state.update_data(user_tg_id=user_tg_id)
