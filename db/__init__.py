from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from .models import *

DATABASE_URL = load_config().database
engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)