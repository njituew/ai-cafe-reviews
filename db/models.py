from datetime import datetime, time
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, func, ForeignKey

from config.enums import *
from datetime import datetime
from pytz import timezone


MOSCOW_TZ = timezone("Europe/Moscow")


class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(MOSCOW_TZ),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(MOSCOW_TZ),
        onupdate=lambda: datetime.now(MOSCOW_TZ)
    )
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'
   
   
class Manager(BaseModel):
    user_id: Mapped[int]
    name: Mapped[str]
 

class Review(BaseModel):
    user_id: Mapped[int]
    user_name: Mapped[str]
    rating: Mapped[int]
    text: Mapped[str]
    tonality: Mapped[ToneEnum]
    readed: Mapped[bool]
    answered: Mapped[bool]
    readed_by: Mapped[int | None] = mapped_column(ForeignKey('managers.user_id'))
    
    # Many-to-one
    manager: Mapped[Manager] = relationship(
        'Manager'
    )