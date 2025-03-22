from datetime import datetime
from functools import wrapper

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, update, delete
from sqlalchemy import desc

from .models import *
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
async def get_review(r_id: int, session: AsyncSession) -> Rewiew:
    rewiew = await session.scalars(
        select(Rewiew).\
        where(Rewiew.id == r_id)
    ).first()
    return rewiew


@connection
async def get_user_reviews(u_id: int, session: AsyncSession) -> list[Rewiew]:
    rewiews = await session.scalars(
        select(Rewiew).\
        where(Rewiew.user_id == u_id)
    ).all()
    return rewiews


@connection
async def add_rewiew(rewiew_model: Rewiew, session: AsyncSession) -> None:
    session.add(rewiew_model)
    await session.commit()
    
    
@connection
async def delete_rewiew(rewiew_model: Rewiew, session: AsyncSession) -> None:
    session.delete(rewiew_model)
    await session.commit()
    
    
@connection
async def get_rewiews_by_time(start: datetime, end: datetime, session: AsyncSession, reverse=False) -> list[Rewiew]:
    rewiews = session.scalars(
        select(Rewiew).\
        where(Rewiew.created_at >= start).\
        where(Rewiew.created_at <= end).\
        order_by((desc(Rewiew.created_at) if reverse else Rewiew.created_at))
    ).all()
    return rewiews


@connection
async def mark_as_readed(rewiew_id: int, mngr_id: int, session: AsyncSession) -> None:
    session.execute(
        update(Rewiew).\
        where(Rewiew.id == rewiew_id).\
        values(readed=True, readed_by=mngr_id)
    )
    session.commit()
    

@connection
async def unreaded_rewiews(session: AsyncSession, reverse=False) -> list[Rewiew]:
    rewiews = session.scalars(
        select(Rewiew).\
        where(Rewiew.readed is True).\
        order_by((desc(Rewiew.created_at) if reverse else Rewiew.created_at))
    )
    return rewiews.all()


@connection
async def get_manager_info(start: datetime, end: datetime, session: AsyncSession, reverse=False) -> list[tuple[Manager, int]]:
    managers = session.scalars(
        select(Manager).\
        where(Manager.created_at >= start).\
        where(Manager.created_at <= end).\
        order_by((desc(Manager.created_at) if reverse else Manager.created_at))
    ).all()
    
    activity = list()
    for mngr in managers:
        mngr_activ = session.query(Rewiew).filter(
            Rewiew.created_at >= start,
            Rewiew.created_at <= end,
            Rewiew.readed is True,
            Rewiew.readed_by == mngr.user_id
        ).count()
        activity.append(mngr_activ)
        
    return zip(managers, activity)
    