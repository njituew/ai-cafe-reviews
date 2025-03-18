from aiogram import types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.utils import is_manager


async def manager_cmd(message: types.Message):
    chat_id = message.chat.id
    if not is_manager(chat_id):
        await message.answer("Вы не менеджер")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Динамика удовлетворённости 📈")],
            [KeyboardButton(text="Дашборд 💩"), KeyboardButton(text="Непрочитанные отзывы 🗣️")],
            [KeyboardButton(text="Профиль менеджера 👩‍💼")]
        ],
        resize_keyboard=True
    )
    await message.answer("Панель менеджера открыта", reply_markup=keyboard)


def register_handlers(dp):
    dp.message.register(manager_cmd, Command("manager"))
