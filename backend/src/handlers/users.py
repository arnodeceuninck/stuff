from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from dependencies import get_db
from src.domain.models import Item, Location, User

router = APIRouter(prefix="/users", tags=["users"])


class UserProfile(BaseModel):
    id: str
    display_name: str | None
    preferred_currency: str


class UserLocationSummary(BaseModel):
    id: str
    name: str
    parent_location_id: str | None
    note: str | None
    item_count: int
    child_location_count: int


async def get_or_create_user(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.id == current_user.sub))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(id=current_user.sub)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


@router.get("/me", response_model=UserProfile)
async def get_me(user: User = Depends(get_or_create_user)) -> UserProfile:
    return UserProfile(
        id=user.id,
        display_name=user.display_name,
        preferred_currency=user.preferred_currency,
    )


@router.get("/me/locations", response_model=list[UserLocationSummary])
async def get_my_locations(
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> list[UserLocationSummary]:
    item_count_subquery = (
        select(Item.location_id.label("location_id"), func.count(Item.id).label("item_count"))
        .where(Item.location_id.is_not(None))
        .group_by(Item.location_id)
        .subquery()
    )
    child_count_subquery = (
        select(
            Location.parent_location_id.label("location_id"),
            func.count(Location.id).label("child_location_count"),
        )
        .where(Location.parent_location_id.is_not(None))
        .group_by(Location.parent_location_id)
        .subquery()
    )

    result = await db.execute(
        select(
            Location.id,
            Location.name,
            Location.parent_location_id,
            Location.note,
            func.coalesce(item_count_subquery.c.item_count, 0).label("item_count"),
            func.coalesce(child_count_subquery.c.child_location_count, 0).label(
                "child_location_count"
            ),
        )
        .outerjoin(item_count_subquery, item_count_subquery.c.location_id == Location.id)
        .outerjoin(child_count_subquery, child_count_subquery.c.location_id == Location.id)
        .where(Location.user_id == user.id)
        .order_by(Location.name, Location.id)
    )

    return [UserLocationSummary(**row) for row in result.mappings().all()]


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    preferred_currency: str | None = None


@router.patch("/me", response_model=UserProfile)
async def update_me(
    body: UpdateProfileRequest,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.preferred_currency is not None:
        user.preferred_currency = body.preferred_currency
    await db.commit()
    await db.refresh(user)
    return UserProfile(
        id=user.id,
        display_name=user.display_name,
        preferred_currency=user.preferred_currency,
    )
