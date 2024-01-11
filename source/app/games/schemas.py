from pydantic import BaseModel

from source.app.games.enums import Order, Sort
from source.core.schemas import PageSchema, PaginationSchema, ResponseSchema


class GameRequest(BaseModel):
    game_name: str
    game_description: str
    game_ranks: list[str]
    game_logo: str


class GameResponse(ResponseSchema):
    game_name: str
    game_description: str
    game_ranks: list[str]
    game_logo: str


class GameUpdateRequest(BaseModel):
    game_name: str | None = None
    game_description: str | None = None
    game_ranks: list[str] | None = None
    game_logo: str | None = None


class GamePage(PageSchema):
    games: list[GameResponse]


class GamePagination(PaginationSchema):
    sort: Sort = Sort.ID
    order: Order = Order.ASC


class GameId(BaseModel):
    game_id: int
