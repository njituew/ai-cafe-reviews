import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.utils import get_bot_token
from src.commands import user, manager

TOKEN = get_bot_token()


bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

manager.register_handlers(dp)
user.register_handlers(dp)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
