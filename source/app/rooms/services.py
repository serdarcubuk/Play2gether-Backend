from math import ceil

from sqlalchemy import asc, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from source.app.profiles.models import Profile
from source.app.rooms.enums import Order, Sort
from source.app.rooms.models import Room
from source.app.rooms.schemas import (
    RoomPage,
    RoomRequest,
    RoomResponse,
    RoomUpdateRequest,
)
from source.app.users.models import User
from source.core.exceptions import bad_request, forbidden, not_found


async def get_room(
    room_id: int,
    db: AsyncSession,
    relation: bool = False,
) -> Room | None:
    if not room_id:
        return None
    query = select(Room).where(Room.id == room_id)
    if not relation:
        return await db.scalar(query)
    query = query.options(selectinload(Room.users))
    if room := await db.scalar(query.options(selectinload(Room.users))):
        user_ids = [user.id for user in room.users]
        users = await db.scalars(
            select(Profile)
            .where(Profile.user_id.in_(user_ids))
            .where(Profile.game_id == room.game_id)
            .options(selectinload(Profile.user))
        )
        user_profiles: list = []
        for user in users:
            user_profiles.append(
                {
                    "id": user.user_id,
                    "username": user.user.username,
                    "user_nickname": user.user_nickname,
                    "user_rank": user.user_rank,
                }
            )
        room.user_profiles = user_profiles
    return room


async def create_room(
    request: RoomRequest, user: User, db: AsyncSession
) -> Room | None:
    if await db.scalar(
        select(Profile)
        .where(Profile.user_id == user.id)
        .where(Profile.game_id == request.game_id)
    ):
        room = Room(**request.model_dump())
        room.owner_id = user.id
        if old_room := await db.scalar(select(Room).where(Room.owner_id == user.id)):
            await db.delete(old_room)
        user.room = room
        try:
            db.add(room)
            await db.commit()
            await db.refresh(room, attribute_names=RoomResponse.model_fields.keys())
        except IntegrityError:
            return None
        return room
    return None


async def update_room(
    payload: RoomUpdateRequest,
    user: User,
    db: AsyncSession,
) -> Room | None:
    if room := await get_room(room_id=user.room_id, db=db):
        if room.owner_id != user.id:
            return forbidden("You are not the owner of the room")
        fields_to_update = payload.model_dump().items()
        for key, value in fields_to_update:
            if value is not None:
                setattr(room, key, value)
        await db.commit()
        await db.refresh(room, attribute_names=RoomResponse.model_fields.keys())
        return room
    return None


async def delete_room(user: User, db: AsyncSession) -> bool:
    if room := await get_room(room_id=user.room_id, db=db):
        if room.owner_id == user.id:
            await db.delete(room)
        user.room_id = None
        await db.commit()
        return True
    return False


async def list_rooms(
    page: int,
    size: int,
    sort: Sort,
    order: Order,
    game_id: int | None,
    db: AsyncSession,
) -> RoomPage:
    order = asc(sort) if order == Order.ASC else desc(sort)

    subquery = (
        select(User.room_id)
        .group_by(User.room_id)
        .having(func.count(User.id) < Room.room_size)
        .lateral()
    )
    query = (
        select(Room)
        .join(subquery, Room.id == subquery.c.room_id)
        .order_by(order)
        .offset((page - 1) * size)
        .limit(size)
        .options(selectinload(Room.users))
    )
    if game_id:
        query = query.where(Room.game_id == game_id)

    rooms = (await db.scalars(query)).all()
    total = len(rooms)

    return RoomPage(
        rooms=rooms,
        page=page,
        size=size,
        total=total,
        pages=(ceil(total / size)),
    )


async def join_room(room_id: int, user: User, db: AsyncSession) -> Room | None:
    if room := await get_room(room_id=room_id, db=db):
        if user.room_id == room_id:
            return bad_request("You already in this room")
        if room.room_size <= await db.scalar(
            select(func.count(User.id)).where(User.room_id == room_id)
        ):
            return bad_request("The room is full")
        if not await db.scalar(
            select(Profile)
            .where(Profile.user_id == user.id)
            .where(Profile.game_id == room.game_id)
        ):
            return not_found(
                f"You need to create a game profile for game {room.game_id}"
            )
        if user.room_id:
            old_room = await db.get(Room, user.room_id)
            if old_room.owner_id == user.id:
                await db.delete(old_room)
        user.room = room
        await db.commit()
        return await get_room(room_id=room_id, db=db, relation=True)
    return None


async def kick_room(
    user_id: int,
    user: User,
    db: AsyncSession,
) -> bool:
    kick_user = await db.get(User, user_id)
    if not kick_user or kick_user.room_id != user.room_id:
        return not_found(f"User '{user_id}' not in the room")
    if kick_user.id == user.id:
        return bad_request("You can not kick yourself")
    if room := await db.get(Room, user.room_id):
        if room.owner_id != user.id:
            return forbidden("You are not the owner of the room")
        kick_user.room_id = None
        await db.commit()
        return True
    return False
