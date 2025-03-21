from typing import Any
from functools import wrapper

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, update, delete

from .models import Rewiew
from . import async_session_maker


def connection(method):
    @wrapper
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
    return wrapper


@connection
def get_review(r_id: int = 0) -> Rewiew:
    rewiew = await session.scalars(
        select(Rewiew).\
        where(Rewiew.id = r_id)
    ).first()
    