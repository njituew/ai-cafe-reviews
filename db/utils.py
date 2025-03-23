from datetime import datetime
from functools import wraps
from typing import Awaitable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, update, delete
from sqlalchemy import desc

from .models import *
from . import async_session_maker


def connection(method: Awaitable):
    @wraps(method)
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
async def add_manager(manager_model: Manager, session: AsyncSession) -> None:
    if not await is_manager(manager_model.user_id):
        session.add(manager_model)
        await session.commit()


@connection
async def is_manager(user_id: int, session: AsyncSession) -> bool:
    existing_manager = await session.scalar(
        select(Manager).where(Manager.user_id == user_id)
    )
    return existing_manager is not None


@connection
async def get_review(r_id: int, session: AsyncSession) -> Review:
    review = await session.scalars(
        select(Review).\
        where(Review.id == r_id)
    )
    return review.first()


@connection
async def get_user_reviews(u_id: int, session: AsyncSession) -> list[Review]:
    reviews = await session.scalars(
        select(Review).\
        where(Review.user_id == u_id)
    )
    return reviews.all()


@connection
async def add_review(review_model: Review, session: AsyncSession) -> None:
    session.add(review_model)
    await session.commit()
    
    
@connection
async def delete_review(review_model: Review, session: AsyncSession) -> None:
    await session.delete(review_model)
    await session.commit()
    
    
@connection
async def get_reviews_by_time(start: datetime, end: datetime, session: AsyncSession, reverse=False) -> list[Review]:
    reviews = await session.scalars(
        select(Review).\
        where(Review.created_at >= start).\
        where(Review.created_at <= end).\
        order_by((desc(Review.created_at) if reverse else Review.created_at))
    )
    return reviews.all()


@connection
async def mark_as_readed(review_id: int, mngr_id: int, session: AsyncSession) -> None:
    await session.execute(
        update(Review).\
        where(Review.id == review_id).\
        values(readed=True, readed_by=mngr_id)
    )
    await session.commit()


@connection
async def mark_as_answered(review_id: int, session: AsyncSession) -> None:
    await session.execute(
        update(Review).\
        where(Review.id == review_id).\
        values(answered=True)
    )
    await session.commit()
    

@connection
async def unreaded_reviews(session: AsyncSession, reverse=False) -> list[Review]:
    reviews = await session.scalars(
        select(Review).\
        where(Review.readed == False).\
        order_by((desc(Review.created_at) if reverse else Review.created_at))
    )
    return reviews.all()


@connection
async def get_manager_info(start: datetime, end: datetime, session: AsyncSession, reverse=False) -> list[tuple[Manager, int]]:
    managers = await session.scalars(
        select(Manager).\
        where(Manager.created_at >= start).\
        where(Manager.created_at <= end).\
        order_by((desc(Manager.created_at) if reverse else Manager.created_at))
    )
    managers = managers.all()
    
    activity = []
    for mngr in managers:
        mngr_activ = await session.scalar(
            select(func.count(Review.id)).\
            where(
                Review.created_at >= start,
                Review.created_at <= end,
                Review.readed == True,
                Review.readed_by == mngr.user_id
            )
        )
        activity.append(mngr_activ)
        
    return list(zip(managers, activity))