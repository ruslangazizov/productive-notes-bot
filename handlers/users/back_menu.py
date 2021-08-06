from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types

from handlers.users.start import reset_state_saving_user_id
from keyboards.default import main_menu
from loader import dp


@dp.message_handler(Text(equals="Главное меню"), state="*")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await reset_state_saving_user_id(state)

    await message.delete()
    await message.answer("<b>Главное меню</b>", reply_markup=main_menu)


@dp.message_handler(Text(equals="Назад"), state="*")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    pass  # TODO: реализовать
