from aiogram import types
from aiogram.filters import Command
from src.utils import is_manager

async def manager_cmd(message: types.Message):
    chat_id = message.chat.id
    if is_manager(chat_id):
        await message.answer("Вы менеджер")
    else:
        await message.answer(f"Вы не менеджер. ID: {chat_id}")

def register_handlers(dp):
    dp.message.register(manager_cmd, Command("manager"))