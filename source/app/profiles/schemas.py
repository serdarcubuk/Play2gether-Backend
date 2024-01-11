from pydantic import BaseModel

from source.app.games.schemas import GameResponse
from source.app.rooms.enums import Order, Sort
from source.core.schemas import PageSchema, PaginationSchema, ResponseSchema


class ProfileRequest(BaseModel):
    game_id: int
    user_nickname: str
    user_rank: str | None = None


class Profile(ResponseSchema):
    user_nickname: str
    user_rank: str | None


class ProfileResponse(Profile):
    game: GameResponse


class ProfileUpdateRequest(BaseModel):
    user_nickname: str | None = None
    user_rank: str | None = None


class ProfilePage(PageSchema):
    profiles: list[ProfileResponse]


class ProfilePagination(PaginationSchema):
    sort: Sort = Sort.ID
    order: Order = Order.ASC


class ProfileId(BaseModel):
    profile_id: int
