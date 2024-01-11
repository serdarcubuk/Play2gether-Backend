from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from source.app.auth.auth import CurrentUser
from source.app.rooms.models import Room
from source.app.rooms.schemas import (
    RoomDetailResponse,
    RoomId,
    RoomPage,
    RoomPagination,
    RoomRequest,
    RoomResponse,
    RoomUpdateRequest,
)
from source.app.rooms.services import (
    create_room,
    delete_room,
    get_room,
    join_room,
    kick_room,
    list_rooms,
    update_room,
)
from source.app.users.schemas import UserId
from source.core.database import get_db
from source.core.exceptions import not_found
from source.core.middlewares import CustomAPIRouter
from source.core.schemas import ExceptionSchema

rooms_router = CustomAPIRouter(prefix="/rooms")


@rooms_router.post(
    "/",
    response_model=RoomResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_201_CREATED,
    tags=["rooms"],
)
async def room_create(
    user: CurrentUser, request: RoomRequest, db: AsyncSession = Depends(get_db)
) -> Room:
    if created_room := await create_room(request=request, user=user, db=db):
        return created_room
    return not_found(f"You need to create a game profile for game {request.game_id}")


@rooms_router.get(
    "/",
    response_model=RoomDetailResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    tags=["rooms"],
)
async def room_get(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Room:
    if user_room := await get_room(room_id=user.room_id, db=db, relation=True):
        return user_room
    return not_found("You are not in the any room")


@rooms_router.patch(
    "/",
    response_model=RoomResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
    },
    tags=["rooms"],
)
async def room_update(
    user: CurrentUser,
    payload: RoomUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> Room:
    if room := await update_room(payload=payload, user=user, db=db):
        return room
    return not_found("You are not in the any room")


@rooms_router.delete(
    "/",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["rooms"],
)
async def room_delete(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> None:
    if not await delete_room(user=user, db=db):
        return not_found("You are not in the any room")


@rooms_router.get(
    "/list",
    response_model=RoomPage,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
    tags=["rooms"],
)
async def rooms_list(
    user: CurrentUser,
    pagination: RoomPagination = Depends(),
    db: AsyncSession = Depends(get_db),
) -> RoomPage:
    return await list_rooms(
        page=pagination.page,
        size=pagination.size,
        sort=pagination.sort,
        order=pagination.order,
        game_id=pagination.game_id,
        db=db,
    )


@rooms_router.get(
    "/look/{room_id}",
    response_model=RoomDetailResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    tags=["rooms"],
)
async def room_look(
    user: CurrentUser, request: RoomId = Depends(), db: AsyncSession = Depends(get_db)
) -> Room:
    if room := await get_room(room_id=request.room_id, db=db, relation=True):
        return room
    return not_found(f"Room '{request.room_id}' not found")


@rooms_router.post(
    "/join/{room_id}",
    response_model=RoomDetailResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    tags=["rooms"],
)
async def room_join(
    user: CurrentUser,
    request: RoomId = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Room:
    if joined_room := await join_room(room_id=request.room_id, user=user, db=db):
        return joined_room
    return not_found(f"Room '{request.room_id}' not found")


@rooms_router.delete(
    "/kick/{user_id}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["rooms"],
)
async def room_kick(
    user: CurrentUser,
    request: UserId = Depends(),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await kick_room(user_id=request.user_id, user=user, db=db):
        return not_found("You are not in the any room")
