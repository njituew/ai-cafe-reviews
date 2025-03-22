import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.utils import get_bot_token
from src.commands.user import user_router
from src.commands.manager import manager_router

TOKEN = get_bot_token()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

dp.include_router(user_router)
dp.include_router(manager_router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
