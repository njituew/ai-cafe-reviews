import os
from dotenv import load_dotenv
import json
from src.logger import logger

"""
Функция для получения токена бота из .env файла
"""
def get_bot_token() -> str:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    # Проверка токена
    if not token:
        logger.critical("BOT_TOKEN is missing in the environment")
        raise ValueError("BOT_TOKEN is missing in the environment")
    logger.info("BOT_TOKEN loaded")
    return token

"""
Функция для проверки наличия прав менеджера у пользователя
"""
MANAGERS = None
def is_manager(chat_id: int, file_path: str = "managers.json") -> bool:
    global MANAGERS
    if MANAGERS is None:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)["managers"]
                MANAGERS = {manager["chat_id"] for manager in data}
        except FileNotFoundError as e:
            logger.error(f"Error loading managers: {e}")
            MANAGERS = set()
        if not MANAGERS:
            logger.warning("There are no managers")
        else:
            logger.info("Managers loaded")
    
    return chat_id in MANAGERS
