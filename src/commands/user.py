from aiogram import types

async def default_cmd(message: types.Message):
    await message.answer(message.text)

def register_handlers(dp):
    dp.message.register(default_cmd)