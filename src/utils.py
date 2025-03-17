import os
from dotenv import load_dotenv
import json

'''
Функция для получения токена бота из .env файла
'''
def get_bot_token() -> str:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    # Проверка токена
    if not token:
        raise ValueError("BOT_TOKEN отсутствует в файле .env")
    return token

'''
Функция для получения id менеджеров из json
'''
MANAGERS = None
def is_manager(chat_id: int, file_path: str = "managers.json") -> bool:
    global MANAGERS
    if MANAGERS is None:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)["managers"]
                MANAGERS = {manager["chat_id"] for manager in data}
        except FileNotFoundError as e:
            print(f"Error loading managers: {e}")
            MANAGERS = set()
    
    return chat_id in MANAGERS
