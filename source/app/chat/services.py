from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.profiles.models import Profile
from source.app.rooms.models import Room
from source.app.users.models import User


async def get_nickname(user: User, db: AsyncSession):
    if not user.room_id:
        return None
    room = await db.scalar(select(Room).where(Room.id == user.room_id))
    profile = await db.scalar(
        select(Profile)
        .where(Profile.user_id == user.id)
        .where(Profile.game_id == room.game_id)
    )
    return profile.user_nickname
