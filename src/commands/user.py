from aiogram import types

async def default(message: types.Message):
    await message.answer(message.text)

def register_handlers(dp):
    dp.message.register(default)