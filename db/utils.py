from typing import Any
from functools import wrapper

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, update, delete

from .models import Rewiew
from . import async_session_maker


def connection(method: callable):
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
async def get_review(r_id: int, session) -> Rewiew:
    rewiew = await session.scalars(
        select(Rewiew).\
        where(Rewiew.id == r_id)
    ).first()
    return rewiew


@connection
async def get_user_reviews(u_id: int, session) -> list[Rewiew]:
    rewiews = await session.scalars(
        select(Rewiew).\
        where(Rewiew.user_id == u_id)
    ).all()
    return rewiews


@connection
async def add_rewiew(rewiew_model: Rewiew, session) -> None:
    session.add(rewiew_model)
    await session.commit()
    
    
@connection
async def delete_rewiew(rewiew_model: Rewiew, session) -> None:
    session.delete(rewiew_model)
    await session.commit() 
    