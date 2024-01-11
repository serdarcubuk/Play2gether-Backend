from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.core.models import Model

if TYPE_CHECKING:
    from source.app.games.models import Game
    from source.app.users.models import User
else:
    User = "User"
    Game = "Game"


class Profile(Model):
    __tablename__ = "Profiles"
    __table_args__ = (UniqueConstraint("user_id", "game_id", name="user_game"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("Users.id"), index=True, primary_key=True
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("Games.id"), index=True, primary_key=True
    )

    user_nickname: Mapped[str | None]
    user_rank: Mapped[str | None]

    user: Mapped[User] = relationship(back_populates="profiles")
    game: Mapped[Game] = relationship(back_populates="profiles")
