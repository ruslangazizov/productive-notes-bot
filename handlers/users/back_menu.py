from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram import types

from keyboards.default import main_menu
from loader import dp


@dp.message_handler(Command("menu"))
@dp.message_handler(Text(equals="Главное меню"), state="*")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await state.reset_state()
    await state.update_data(user_tg_id=message.from_user.id)

    await message.delete()
    await message.answer("<b>Главное меню</b>", reply_markup=main_menu)
