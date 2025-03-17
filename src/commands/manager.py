from aiogram import types
from aiogram.filters import Command
from src.utils import load_managers

async def manager_cmd(message: types.Message):
    chat_id = message.chat.id
    if chat_id in load_managers():
        await message.answer("Вы менеджер")
    else:
        await message.answer(f"Вы не менеджер. ID: {chat_id}")

def register_handlers(dp):
    dp.message.register(manager_cmd, Command("manager"))