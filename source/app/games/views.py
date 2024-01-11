from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.auth.auth import Admin, CurrentUser
from source.app.games.models import Game
from source.app.games.schemas import (
    GameId,
    GamePage,
    GamePagination,
    GameRequest,
    GameResponse,
    GameUpdateRequest,
)
from source.app.games.services import (
    create_game,
    delete_game,
    get_game,
    list_games,
    update_game,
)
from source.core.database import get_db
from source.core.exceptions import conflict, not_found
from source.core.middlewares import CustomAPIRouter
from source.core.schemas import ExceptionSchema

games_router = CustomAPIRouter(prefix="/games")


@games_router.post(
    "/",
    response_model=GameResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_201_CREATED,
    tags=["games"],
)
async def game_create_admin(
    user: Admin, request: GameRequest, db: AsyncSession = Depends(get_db)
) -> Game:
    if created_game := await create_game(request=request, db=db):
        return created_game
    return conflict(f"Game '{request.game_name}' already exists")


@games_router.get(
    "/{game_id}",
    response_model=GameResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    tags=["games"],
)
async def game_get(
    user: CurrentUser, request: GameId = Depends(), db: AsyncSession = Depends(get_db)
) -> Game:
    if game := await get_game(game_id=request.game_id, db=db):
        return game
    return not_found(f"Game '{request.game_id}' not found")


@games_router.patch(
    "/{game_id}",
    response_model=GameResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
    },
    tags=["games"],
)
async def game_update_admin(
    user: Admin,
    payload: GameUpdateRequest,
    request: GameId = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Game:
    if updated_game := await update_game(
        game_id=request.game_id, payload=payload, db=db
    ):
        return updated_game
    return not_found(f"Game '{request.game_id}' not found")


@games_router.delete(
    "/{game_id}",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["games"],
)
async def game_delete_admin(
    user: Admin, request: GameId = Depends(), db: AsyncSession = Depends(get_db)
) -> None:
    if not await delete_game(game_id=request.game_id, db=db):
        return not_found(f"Game '{request.game_id}' not found")


@games_router.get(
    "/",
    response_model=GamePage,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
    tags=["games"],
)
async def games_list(
    user: CurrentUser,
    pagination: GamePagination = Depends(),
    db: AsyncSession = Depends(get_db),
) -> GamePage:
    return await list_games(
        page=pagination.page,
        size=pagination.size,
        sort=pagination.sort,
        order=pagination.order,
        db=db,
    )
