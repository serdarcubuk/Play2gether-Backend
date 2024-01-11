from math import ceil

from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from source.app.games.models import Game
from source.app.profiles.models import Profile
from source.app.profiles.schemas import (
    ProfilePage,
    ProfileRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from source.app.rooms.enums import Order, Sort
from source.app.rooms.models import Room
from source.app.rooms.services import delete_room
from source.app.users.models import User
from source.core.exceptions import conflict


async def get_profile(
    profile_id: int, user: User, db: AsyncSession, relation: bool = True
) -> Profile:
    query = (
        select(Profile)
        .where(Profile.id == profile_id)
        .where(Profile.user_id == user.id)
    )
    if relation:
        query = query.options(selectinload(Profile.game))
    return await db.scalar(query)


async def create_profile(
    request: ProfileRequest, user: User, db: AsyncSession
) -> Profile | None:
    if game := await db.get(Game, request.game_id):
        profile = Profile(
            user=user,
            game=game,
            user_nickname=request.user_nickname,
            user_rank=request.user_rank,
        )
        try:
            db.add(profile)
            await db.commit()
            await db.refresh(
                profile, attribute_names=ProfileResponse.model_fields.keys()
            )
            return profile
        except IntegrityError:
            return conflict("You already have a profile in this game")
    return None


async def update_profile(
    profile_id: int,
    payload: ProfileUpdateRequest,
    user: User,
    db: AsyncSession,
) -> Profile | None:
    if profile := await get_profile(profile_id=profile_id, user=user, db=db):
        fields_to_update = payload.model_dump().items()
        for key, value in fields_to_update:
            if value is not None:
                setattr(profile, key, value)
        await db.commit()
        await db.refresh(profile)
        return profile
    return None


async def delete_profile(profile_id: int, user: User, db: AsyncSession) -> bool:
    if profile := await get_profile(
        profile_id=profile_id, user=user, db=db, relation=False
    ):
        if user.room_id:
            room = await db.get(Room, user.room_id)
            if room and room.game_id == profile.game_id:
                await delete_room(user=user, db=db)
        await db.delete(profile)
        await db.commit()
        return True
    return False


async def list_profiles(
    user_id: int, page: int, size: int, sort: Sort, order: Order, db: AsyncSession
) -> ProfilePage:
    order = asc(sort) if order == Order.ASC else desc(sort)

    profiles = (
        await db.scalars(
            select(Profile)
            .filter(Profile.user_id == user_id)
            .order_by(order)
            .offset((page - 1) * size)
            .limit(size)
            .options(selectinload(Profile.game))
        )
    ).all()
    total = len(profiles)

    return ProfilePage(
        profiles=profiles,
        page=page,
        size=size,
        total=total,
        pages=(ceil(total / size)),
    )
