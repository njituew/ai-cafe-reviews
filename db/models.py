from datetime import datetime, time
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, func, ForeignKey

from config.enums import *


class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'
   
   
class Manager(BaseModel):
    user_id: Mapped[int]
    name: Mapped[str]
 

class Review(BaseModel):
    user_id: Mapped[int]
    rating: Mapped[int]
    text: Mapped[str]
    tonality: Mapped[ToneEnum]
    readed: Mapped[bool]
    readed_by: Mapped[int | None] = mapped_column(ForeignKey('managers.user_id'))
    
    # Many-to-one
    manager: Mapped[Manager] = relationship(
        'Manager'
    )