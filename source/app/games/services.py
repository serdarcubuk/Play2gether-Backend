from math import ceil

from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.games.enums import Order, Sort
from source.app.games.models import Game
from source.app.games.schemas import GamePage, GameRequest, GameUpdateRequest
from source.core.exceptions import conflict


async def get_game(game_id: int, db: AsyncSession) -> Game | None:
    return await db.get(Game, game_id)


async def create_game(request: GameRequest, db: AsyncSession) -> Game | None:
    try:
        game = Game(**request.model_dump())
        db.add(game)
        await db.commit()
        await db.refresh(game)
        return game
    except IntegrityError:
        return None


async def update_game(
    game_id: int,
    payload: GameUpdateRequest,
    db: AsyncSession,
) -> Game | None:
    if game := await get_game(game_id=game_id, db=db):
        try:
            fields_to_update = payload.model_dump().items()
            for key, value in fields_to_update:
                if value is not None:
                    setattr(game, key, value)
            await db.commit()
            await db.refresh(game)
            return game
        except IntegrityError:
            return conflict(f"Game '{payload.game_name}' already exists")
    return None


async def delete_game(game_id: int, db: AsyncSession) -> bool:
    if game := await get_game(game_id=game_id, db=db):
        await db.delete(game)
        await db.commit()
        return True
    return False


async def list_games(
    page: int, size: int, sort: Sort, order: Order, db: AsyncSession
) -> GamePage:
    order = asc(sort) if order == Order.ASC else desc(sort)

    games = (
        await db.scalars(
            select(Game).order_by(order).offset((page - 1) * size).limit(size)
        )
    ).all()
    total = len(games)

    return GamePage(
        games=games,
        page=page,
        size=size,
        total=total,
        pages=(ceil(total / size)),
    )
