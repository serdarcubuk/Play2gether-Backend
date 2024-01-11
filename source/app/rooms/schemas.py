from pydantic import BaseModel, ConfigDict, Field, model_validator

from source.app.rooms.enums import Order, Sort
from source.app.users.schemas import UserProfile
from source.core.schemas import PageSchema, PaginationSchema, ResponseSchema


class RoomRequest(BaseModel):
    game_id: int
    room_name: str
    room_description: str | None = None
    room_ranks: list[str] | None = None
    room_size: int = Field(default=5, ge=1, le=100)


class RoomResponse(ResponseSchema):
    game_id: int
    owner_id: int
    room_name: str
    room_description: str | None
    room_ranks: list[str] | None
    room_size: int
    users: list | int = Field(alias="number_of_users")

    @model_validator(mode="after")
    def validator(cls, values: "RoomResponse") -> "RoomResponse":
        values.users = len(values.users)  # type: ignore
        return values

    model_config = ConfigDict(populate_by_name=True)


class RoomDetailResponse(ResponseSchema):
    game_id: int
    owner_id: int
    room_name: str
    room_description: str | None
    room_ranks: list[str] | None
    room_size: int
    number_of_users: int | None = None
    user_profiles: list[UserProfile]

    @model_validator(mode="after")
    def validator(cls, values: "RoomDetailResponse") -> "RoomDetailResponse":
        values.number_of_users = len(values.user_profiles)
        return values


class RoomUpdateRequest(BaseModel):
    room_name: str | None = None
    room_description: str | None = None
    room_ranks: list[str] | None = None
    room_size: int | None = None


class RoomPage(PageSchema):
    rooms: list[RoomResponse]


class RoomPagination(PaginationSchema):
    sort: Sort = Sort.ID
    order: Order = Order.ASC
    game_id: int | None = None


class RoomId(BaseModel):
    room_id: int
