from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Model(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, unique=True, index=True, sort_order=-1
    )
    create_date: Mapped[datetime] = mapped_column(default=func.now(), index=True)
    update_date: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), index=True
    )
