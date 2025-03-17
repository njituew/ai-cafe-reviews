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
def load_managers(file_path: str = "managers.json") -> set[int]:
    if MANAGERS is not None:
        return MANAGERS
    else:
        try:
            with open(file_path, "r") as f:
                managers = json.load(f)["managers"]
                return {manager["chat_id"] for manager in managers}
        except FileNotFoundError as e:
            print(f"Error loading managers: {e}")
            return set()
