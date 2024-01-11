from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.core.models import Model

if TYPE_CHECKING:
    from source.app.profiles.models import Profile
    from source.app.rooms.models import Room
else:
    Profile = "Profile"
    Room = "Room"


class User(Model):
    __tablename__ = "Users"

    room_id: Mapped[int | None] = mapped_column(ForeignKey("Rooms.id"), index=True)

    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    email: Mapped[str]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    active: Mapped[bool]
    role: Mapped[str]
    password_timestamp: Mapped[float]

    profiles: Mapped[list[Profile]] = relationship(cascade="all, delete-orphan")
    room: Mapped[Room] = relationship(
        back_populates="users", primaryjoin="User.room_id == Room.id"
    )
    own_room: Mapped[Room] = relationship(
        back_populates="owner",
        primaryjoin="User.id == Room.owner_id",
        cascade="all, delete-orphan",
        post_update=True,
    )
