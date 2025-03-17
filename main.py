import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.utils import get_bot_token
from src.commands import default

TOKEN = get_bot_token()

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.message.register(default)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    print("Bot is running...")
    asyncio.run(main())