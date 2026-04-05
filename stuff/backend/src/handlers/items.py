from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend_framework.dependencies import get_db

from src.domain.models import (
    Attachment,
    Comment,
    Item,
    Location,
    Merchant,
    OwnershipType,
    Price,
    PriceFrequency,
    PriceKind,
    User,
)
from src.handlers.users import get_or_create_user

router = APIRouter(tags=["items"])


class LocationSummary(BaseModel):
    id: str
    name: str
    parent_location_id: str | None
    note: str | None


class MerchantSummary(BaseModel):
    id: str
    name: str
    website: str | None
    note: str | None


class AttachmentSummary(BaseModel):
    id: str
    item_id: str
    filename: str
    url: str
    upload_date: datetime | None


class CommentSummary(BaseModel):
    id: str
    item_id: str
    user_id: str | None
    content: str
    created_at: datetime | None


class PriceSummary(BaseModel):
    id: str
    item_id: str
    amount: Decimal
    currency: str
    kind: PriceKind
    frequency: PriceFrequency | None


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str | None
    user_id: str | None
    location_id: str | None
    ownership_type: OwnershipType
    linked_location_id: str | None
    purchased_date: datetime | None
    merchant_id: str | None
    primary_image_id: str | None
    location: LocationSummary | None
    linked_location: LocationSummary | None
    merchant: MerchantSummary | None
    attachments: list[AttachmentSummary]
    comments: list[CommentSummary]
    price: PriceSummary | None
    primary_image: AttachmentSummary | None


class CreateItemRequest(BaseModel):
    name: str
    description: str | None = None
    location_id: str | None = None
    ownership_type: OwnershipType = OwnershipType.OWNED
    linked_location_id: str | None = None
    purchased_date: datetime | None = None
    merchant_id: str | None = None


class UpdateItemRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    location_id: str | None = None
    ownership_type: OwnershipType | None = None
    linked_location_id: str | None = None
    purchased_date: datetime | None = None
    merchant_id: str | None = None
    primary_image_id: str | None = None


class CreateCommentRequest(BaseModel):
    content: str


def _item_load_options() -> list:
    return [
        selectinload(Item.location),
        selectinload(Item.linked_location),
        selectinload(Item.merchant),
        selectinload(Item.attachments),
        selectinload(Item.comments),
        selectinload(Item.price),
        selectinload(Item.primary_image),
    ]


def _to_location_summary(location: Location | None) -> LocationSummary | None:
    if location is None:
        return None
    return LocationSummary(
        id=location.id,
        name=location.name,
        parent_location_id=location.parent_location_id,
        note=location.note,
    )


def _to_merchant_summary(merchant: Merchant | None) -> MerchantSummary | None:
    if merchant is None:
        return None
    return MerchantSummary(
        id=merchant.id,
        name=merchant.name,
        website=merchant.website,
        note=merchant.note,
    )


def _to_attachment_summary(attachment: Attachment) -> AttachmentSummary:
    return AttachmentSummary(
        id=attachment.id,
        item_id=attachment.item_id,
        filename=attachment.filename,
        url=attachment.url,
        upload_date=attachment.upload_date,
    )


def _to_comment_summary(comment: Comment) -> CommentSummary:
    return CommentSummary(
        id=comment.id,
        item_id=comment.item_id,
        user_id=comment.user_id,
        content=comment.content,
        created_at=comment.created_at,
    )


def _to_price_summary(price: Price | None) -> PriceSummary | None:
    if price is None:
        return None
    return PriceSummary(
        id=price.id,
        item_id=price.item_id,
        amount=price.amount,
        currency=price.currency,
        kind=price.kind,
        frequency=price.frequency,
    )


def _to_item_response(item: Item) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        user_id=item.user_id,
        location_id=item.location_id,
        ownership_type=item.ownership_type,
        linked_location_id=item.linked_location_id,
        purchased_date=item.purchased_date,
        merchant_id=item.merchant_id,
        primary_image_id=item.primary_image_id,
        location=_to_location_summary(item.location),
        linked_location=_to_location_summary(item.linked_location),
        merchant=_to_merchant_summary(item.merchant),
        attachments=[_to_attachment_summary(attachment) for attachment in item.attachments],
        comments=[_to_comment_summary(comment) for comment in item.comments],
        price=_to_price_summary(item.price),
        primary_image=(
            _to_attachment_summary(item.primary_image) if item.primary_image is not None else None
        ),
    )


async def _ensure_location_belongs_to_user(
    *,
    location_id: str | None,
    user_id: str,
    db: AsyncSession,
    field_name: str,
) -> None:
    if location_id is None:
        return

    location = await db.scalar(
        select(Location).where(Location.id == location_id, Location.user_id == user_id)
    )
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{field_name} not found for current user",
        )


async def _ensure_merchant_exists(merchant_id: str | None, db: AsyncSession) -> None:
    if merchant_id is None:
        return

    merchant = await db.scalar(select(Merchant.id).where(Merchant.id == merchant_id))
    if merchant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="merchant not found",
        )


async def _get_owned_item(item_id: str, user_id: str, db: AsyncSession) -> Item:
    result = await db.execute(
        select(Item)
        .options(*_item_load_options())
        .where(Item.id == item_id, Item.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return item


@router.get("/locations/{location_id}/items", response_model=list[ItemResponse])
async def get_items_for_location(
    location_id: str,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> list[ItemResponse]:
    await _ensure_location_belongs_to_user(
        location_id=location_id,
        user_id=user.id,
        db=db,
        field_name="location_id",
    )

    result = await db.execute(
        select(Item)
        .options(*_item_load_options())
        .where(Item.user_id == user.id, Item.location_id == location_id)
        .order_by(Item.name, Item.id)
    )
    return [_to_item_response(item) for item in result.scalars().all()]


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: CreateItemRequest,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    await _ensure_location_belongs_to_user(
        location_id=body.location_id,
        user_id=user.id,
        db=db,
        field_name="location_id",
    )
    await _ensure_location_belongs_to_user(
        location_id=body.linked_location_id,
        user_id=user.id,
        db=db,
        field_name="linked_location_id",
    )
    await _ensure_merchant_exists(body.merchant_id, db)

    item = Item(
        id=str(uuid4()),
        user_id=user.id,
        name=body.name,
        description=body.description,
        location_id=body.location_id,
        ownership_type=body.ownership_type,
        linked_location_id=body.linked_location_id,
        purchased_date=body.purchased_date,
        merchant_id=body.merchant_id,
    )
    db.add(item)
    await db.commit()

    return _to_item_response(await _get_owned_item(item.id, user.id, db))


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item_detail(
    item_id: str,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    item = await _get_owned_item(item_id, user.id, db)
    return _to_item_response(item)


@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    body: UpdateItemRequest,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    item = await _get_owned_item(item_id, user.id, db)

    fields_to_update = body.model_fields_set

    if "location_id" in fields_to_update:
        await _ensure_location_belongs_to_user(
            location_id=body.location_id,
            user_id=user.id,
            db=db,
            field_name="location_id",
        )
    if "linked_location_id" in fields_to_update:
        await _ensure_location_belongs_to_user(
            location_id=body.linked_location_id,
            user_id=user.id,
            db=db,
            field_name="linked_location_id",
        )
    if "merchant_id" in fields_to_update:
        await _ensure_merchant_exists(body.merchant_id, db)

    if "primary_image_id" in fields_to_update and body.primary_image_id is not None:
        attachment = await db.scalar(
            select(Attachment).where(
                Attachment.id == body.primary_image_id,
                Attachment.item_id == item.id,
            )
        )
        if attachment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="primary_image_id does not belong to this item",
            )

    if "name" in fields_to_update and body.name is not None:
        item.name = body.name
    if "description" in fields_to_update:
        item.description = body.description
    if "location_id" in fields_to_update:
        item.location_id = body.location_id
    if "ownership_type" in fields_to_update and body.ownership_type is not None:
        item.ownership_type = body.ownership_type
    if "linked_location_id" in fields_to_update:
        item.linked_location_id = body.linked_location_id
    if "purchased_date" in fields_to_update:
        item.purchased_date = body.purchased_date
    if "merchant_id" in fields_to_update:
        item.merchant_id = body.merchant_id
    if "primary_image_id" in fields_to_update:
        item.primary_image_id = body.primary_image_id

    await db.commit()

    return _to_item_response(await _get_owned_item(item.id, user.id, db))


@router.patch("/items/{item_id}", response_model=ItemResponse)
async def patch_item(
    item_id: str,
    body: UpdateItemRequest,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    return await update_item(item_id=item_id, body=body, user=user, db=db)


@router.post(
    "/items/{item_id}/comments",
    response_model=CommentSummary,
    status_code=status.HTTP_201_CREATED,
)
async def create_item_comment(
    item_id: str,
    body: CreateCommentRequest,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> CommentSummary:
    item = await _get_owned_item(item_id, user.id, db)
    comment_content = body.content.strip()
    if not comment_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="content cannot be empty",
        )

    comment = Comment(
        id=str(uuid4()),
        item_id=item.id,
        user_id=user.id,
        content=comment_content,
        created_at=datetime.utcnow(),
    )
    db.add(comment)
    await db.commit()

    return _to_comment_summary(comment)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(
    item_id: str,
    user: User = Depends(get_or_create_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    item = await _get_owned_item(item_id, user.id, db)

    await db.execute(delete(Attachment).where(Attachment.item_id == item.id))
    await db.execute(delete(Comment).where(Comment.item_id == item.id))
    await db.execute(delete(Price).where(Price.item_id == item.id))
    await db.delete(item)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
