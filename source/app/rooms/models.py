from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.core.models import Model

if TYPE_CHECKING:
    from source.app.games.models import Game
    from source.app.users.models import User
else:
    Game = "Game"
    User = "User"


class Room(Model):
    __tablename__ = "Rooms"

    game_id: Mapped[int] = mapped_column(ForeignKey("Games.id"), index=True)
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey(column="Users.id", use_alter=True), index=True
    )

    room_name: Mapped[str] = mapped_column(index=True)
    room_description: Mapped[str | None]
    room_ranks: Mapped[list[str]] = mapped_column(ARRAY(String))
    room_size: Mapped[int]

    game: Mapped[Game] = relationship(back_populates="rooms")
    owner: Mapped[User] = relationship(
        back_populates="own_room",
        primaryjoin="User.id == Room.owner_id",
        post_update=True,
    )
    users: Mapped[list[User]] = relationship(primaryjoin="User.room_id == Room.id")
