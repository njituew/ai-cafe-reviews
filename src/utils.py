from config import load_config
import json
from src.logger import logger
from db.models import Manager
from db.utils import add_manager


def get_bot_token() -> str:
    conf = load_config()
    token = conf.bot_token

    # Проверка токена
    if not token:
        logger.critical("BOT_TOKEN is missing in the environment")
        raise ValueError("BOT_TOKEN is missing in the environment")
    logger.info("BOT_TOKEN loaded")
    return token


async def load_managers():
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
