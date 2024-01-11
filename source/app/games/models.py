from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.core.models import Model

if TYPE_CHECKING:
    from source.app.profiles.models import Profile
    from source.app.rooms.models import Room
else:
    Room = "Room"
    Profile = "Profile"


class Game(Model):
    __tablename__ = "Games"

    game_name: Mapped[str] = mapped_column(unique=True, index=True)
    game_description: Mapped[str]
    game_ranks: Mapped[list[str]] = mapped_column(ARRAY(String))
    game_logo: Mapped[str]

    rooms: Mapped[list[Room]] = relationship(cascade="all, delete-orphan")
    profiles: Mapped[list[Profile]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )
