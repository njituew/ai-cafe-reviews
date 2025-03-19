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
            [KeyboardButton(text="Непрочитанные отзывы 🗣️", callback_data="unread_reviews")],
            [KeyboardButton(text="Дашборд 💻", callback_data="dashboard"),
             KeyboardButton(text="Динамика удовлетворённости 📈", callback_data="satisfaction_dynamic")],
            [KeyboardButton(text="Профиль менеджера 👩‍💼", callback_data="manager_profile")]
        ],
        resize_keyboard=True
    )
    await message.answer("Панель менеджера открыта", reply_markup=keyboard)


def register_handlers(dp):
    dp.message.register(manager_cmd, Command("manager"))
