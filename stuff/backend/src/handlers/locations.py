from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_framework.dependencies import get_db
from src.domain.models import Item, Location, OwnershipType, User
from src.handlers.users import get_or_create_user

router = APIRouter(prefix="/locations", tags=["locations"])


class LocationListSummary(BaseModel):
    id: str
    name: str
    parent_location_id: str | None
    note: str | None
    item_count: int
    child_location_count: int


class LocationItemSummary(BaseModel):
    id: str
    name: str
    description: str | None
    ownership_type: OwnershipType


class LocationDetailResponse(BaseModel):
    id: str
    name: str
    parent_location_id: str | None
    note: str | None
    breadcrumb: list[LocationListSummary]
    child_locations: list[LocationListSummary]
    items: list[LocationItemSummary]


async def _get_owned_location(location_id: str, user_id: str, db: AsyncSession) -> Location:
    location = await db.scalar(
        select(Location).where(Location.id == location_id, Location.user_id == user_id)
    )
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="location not found")
    return location


@router.get("/{location_id}", response_model=LocationDetailResponse)
async def get_location_detail(
    location_id: str,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> LocationDetailResponse:
    location = await _get_owned_location(location_id, user.id, db)

    item_count_subquery = (
        select(Item.location_id.label("location_id"), func.count(Item.id).label("item_count"))
        .where(Item.location_id.is_not(None), Item.user_id == user.id)
        .group_by(Item.location_id)
        .subquery()
    )
    child_count_subquery = (
        select(
            Location.parent_location_id.label("location_id"),
            func.count(Location.id).label("child_location_count"),
        )
        .where(Location.parent_location_id.is_not(None), Location.user_id == user.id)
        .group_by(Location.parent_location_id)
        .subquery()
    )

    child_result = await db.execute(
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
        .where(Location.user_id == user.id, Location.parent_location_id == location.id)
        .order_by(Location.name, Location.id)
    )

    item_result = await db.execute(
        select(Item.id, Item.name, Item.description, Item.ownership_type)
        .where(Item.user_id == user.id, Item.location_id == location.id)
        .order_by(Item.name, Item.id)
    )

    location_lookup_result = await db.execute(
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
    )

    by_id = {row.id: row for row in location_lookup_result}

    breadcrumb: list[LocationListSummary] = []
    current = by_id.get(location.id)
    while current is not None:
        breadcrumb.append(
            LocationListSummary(
                id=current.id,
                name=current.name,
                parent_location_id=current.parent_location_id,
                note=current.note,
                item_count=current.item_count,
                child_location_count=current.child_location_count,
            )
        )
        current = by_id.get(current.parent_location_id)
    breadcrumb.reverse()

    child_locations = [LocationListSummary(**row._mapping) for row in child_result]
    items = [LocationItemSummary(**row._mapping) for row in item_result]

    return LocationDetailResponse(
        id=location.id,
        name=location.name,
        parent_location_id=location.parent_location_id,
        note=location.note,
        breadcrumb=breadcrumb,
        child_locations=child_locations,
        items=items,
    )


class CreateLocationRequest(BaseModel):
    name: str
    parent_location_id: str | None = None
    note: str | None = None


class UpdateLocationRequest(BaseModel):
    name: str | None = None
    note: str | None = None


class LocationResponse(BaseModel):
    id: str
    name: str
    parent_location_id: str | None
    note: str | None


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    body: CreateLocationRequest,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    if body.parent_location_id is not None:
        parent = await db.scalar(
            select(Location).where(
                Location.id == body.parent_location_id,
                Location.user_id == user.id,
            )
        )
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="parent location not found",
            )

    location = Location(
        id=str(uuid4()),
        user_id=user.id,
        name=body.name,
        parent_location_id=body.parent_location_id,
        note=body.note,
    )
    db.add(location)
    await db.commit()

    return LocationResponse(
        id=location.id,
        name=location.name,
        parent_location_id=location.parent_location_id,
        note=location.note,
    )


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: str,
    body: UpdateLocationRequest,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    location = await _get_owned_location(location_id, user.id, db)

    for field in body.model_fields_set:
        setattr(location, field, getattr(body, field))

    await db.commit()

    return LocationResponse(
        id=location.id,
        name=location.name,
        parent_location_id=location.parent_location_id,
        note=location.note,
    )


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: str,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    location = await _get_owned_location(location_id, user.id, db)

    child_count = await db.scalar(
        select(func.count(Location.id)).where(
            Location.parent_location_id == location_id,
            Location.user_id == user.id,
        )
    )
    item_count = await db.scalar(
        select(func.count(Item.id)).where(
            Item.location_id == location_id,
            Item.user_id == user.id,
        )
    )

    if child_count > 0 or item_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Location still contains items or sub-locations. Move or delete them first.",
        )

    await db.delete(location)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
