from config import load_config
import json
from src.logger import logger
from db.models import Manager
from db.utils import add_manager, is_manager
from aiogram import Bot
from aiogram.types import BotCommand


def get_bot_token() -> str:
    conf = load_config()
    token = conf.bot_token

    # Проверка токена
    if not token:
        logger.critical("BOT_TOKEN is missing in the environment")
        raise ValueError("BOT_TOKEN is missing in the environment")
    logger.info("BOT_TOKEN loaded")
    return token


async def load_managers() -> None:
    managers = []
    with open("managers.json", "r") as f:
        data = json.load(f)["managers"]
        managers = [
            {"chat_id": manager["chat_id"], "name": manager["name"]} for manager in data
        ]
    
    for manager in managers:
        manager_obj = Manager(user_id=manager["chat_id"], name=manager["name"])
        await add_manager(manager_obj)
    
    logger.info(f"Managers loaded. Total: {len(managers)}")


async def set_commands(bot: Bot, user_id: int) -> None:
    commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="menu", description="Открыть главное меню"),
        BotCommand(command="add_review", description="Оставить отзыв"),
        BotCommand(command="delete_review", description="Удалить отзыв"),
        BotCommand(command="view_reviews", description="Посмотреть свои отзывы")
    ]
    if await is_manager(user_id):
        commands.extend([
            BotCommand(command="manager", description="Открыть панель менеджера"),
            BotCommand(command="unread_reviews", description="Посмотреть непрочитанные отзывы"),
            BotCommand(command="dashboard", description="Открыть дашборд"),
            BotCommand(command="manager_statistics", description="Посмотреть статистику менеджеров")
        ])
    await bot.set_my_commands(commands)
    logger.info("Commands set")