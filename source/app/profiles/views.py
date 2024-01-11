from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from source.app.auth.auth import CurrentUser
from source.app.profiles.models import Profile
from source.app.profiles.schemas import (
    ProfileId,
    ProfilePage,
    ProfilePagination,
    ProfileRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from source.app.profiles.services import (
    create_profile,
    delete_profile,
    get_profile,
    list_profiles,
    update_profile,
)
from source.core.database import get_db
from source.core.exceptions import not_found
from source.core.middlewares import CustomAPIRouter
from source.core.schemas import ExceptionSchema

profiles_router = CustomAPIRouter(prefix="/profiles")


@profiles_router.post(
    "/",
    response_model=ProfileResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_201_CREATED,
    tags=["profiles"],
)
async def profile_create(
    user: CurrentUser, request: ProfileRequest, db: AsyncSession = Depends(get_db)
) -> Profile:
    if created_profile := await create_profile(request=request, user=user, db=db):
        return created_profile
    return not_found(f"'Game {request.game_id}' not found")


@profiles_router.get(
    "/{profile_id}",
    response_model=ProfileResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    tags=["profiles"],
)
async def profile_get(
    user: CurrentUser,
    request: ProfileId = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Profile:
    if profile := await get_profile(profile_id=request.profile_id, user=user, db=db):
        return profile
    return not_found(f"Profile '{request.profile_id}' not found")


@profiles_router.patch(
    "/{profile_id}",
    response_model=ProfileResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    tags=["profiles"],
)
async def profile_update(
    user: CurrentUser,
    payload: ProfileUpdateRequest,
    request: ProfileId = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Profile:
    if updated_profile := await update_profile(
        profile_id=request.profile_id, payload=payload, user=user, db=db
    ):
        return updated_profile
    return not_found(f"Profile '{request.profile_id}' not found")


@profiles_router.delete(
    "/{profile_id}",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["profiles"],
)
async def profile_delete(
    user: CurrentUser,
    request: ProfileId = Depends(),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await delete_profile(profile_id=request.profile_id, user=user, db=db):
        return not_found(f"Profile '{request.profile_id}' not found")


@profiles_router.get(
    "/",
    response_model=ProfilePage,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
    tags=["profiles"],
)
async def profile_list(
    user: CurrentUser,
    pagination: ProfilePagination = Depends(),
    db: AsyncSession = Depends(get_db),
) -> ProfilePage:
    return await list_profiles(
        user_id=user.id,
        page=pagination.page,
        size=pagination.size,
        sort=pagination.sort,
        order=pagination.order,
        db=db,
    )
