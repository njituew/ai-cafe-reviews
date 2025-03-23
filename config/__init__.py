from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    database: str
    bot_token: str
    groq_key: str


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        database=env('DATABASE_DSN'),
        bot_token=env('BOT_TOKEN'),
        groq_key=env('GROQ_API_KEY')
    )