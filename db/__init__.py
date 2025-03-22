from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from .models import *
from config import load_config

DATABASE_URL = 'sqlite+aiosqlite:///app.db'
print(DATABASE_URL)
engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)