from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.mixins import Base


class PriceKind(str, Enum):
    PURCHASE = "PURCHASE"
    ESTIMATED_PURCHASE = "ESTIMATED_PURCHASE"
    RENTAL = "RENTAL"


class PriceFrequency(str, Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class OwnershipType(str, Enum):
    OWNED = "OWNED"
    RENTED_OR_BORROWED = "RENBOW"
    WANTED = "WANTED"
    NEEDED = "NEEDED"


class User(Base):
    """Stuff-project-specific user profile. The primary key is the same user_id
    issued by the auth-service so no join between services is needed.
    Credentials (email, password) live in the auth-service only."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # App-specific settings below — add more as needed
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferred_currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)

    locations: Mapped[List["Location"]] = relationship(back_populates="user")
    items: Mapped[List["Item"]] = relationship(back_populates="user")
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["Item"]] = relationship(back_populates="merchant")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    parent_location_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("locations.id"), nullable=True
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="locations")
    parent_location: Mapped[Optional["Location"]] = relationship(
        "Location", remote_side=[id], back_populates="child_locations"
    )
    child_locations: Mapped[List["Location"]] = relationship(
        "Location", back_populates="parent_location"
    )
    items: Mapped[List["Item"]] = relationship(
        back_populates="location", foreign_keys="Item.location_id"
    )
    linked_item: Mapped[Optional["Item"]] = relationship(
        back_populates="linked_location",
        foreign_keys="Item.linked_location_id",
        uselist=False,
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("locations.id"), nullable=True
    )
    ownership_type: Mapped[OwnershipType] = mapped_column(
        SQLEnum(OwnershipType, name="ownership_type_enum"),
        default=OwnershipType.OWNED,
        nullable=False,
    )
    linked_location_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("locations.id"), nullable=True, unique=True
    )

    purchased_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    merchant_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("merchants.id"), nullable=True
    )
    primary_image_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("attachments.id"), nullable=True
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="items")
    location: Mapped[Optional[Location]] = relationship(
        back_populates="items", foreign_keys=[location_id]
    )
    linked_location: Mapped[Optional[Location]] = relationship(
        back_populates="linked_item", foreign_keys=[linked_location_id]
    )
    merchant: Mapped[Optional[Merchant]] = relationship(back_populates="items")

    attachments: Mapped[List["Attachment"]] = relationship(
        back_populates="item", foreign_keys="Attachment.item_id"
    )
    comments: Mapped[List["Comment"]] = relationship(back_populates="item")
    price: Mapped[Optional["Price"]] = relationship(back_populates="item", uselist=False)
    primary_image: Mapped[Optional["Attachment"]] = relationship(
        foreign_keys=[primary_image_id], post_update=True
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    upload_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    item: Mapped[Item] = relationship(back_populates="attachments", foreign_keys=[item_id])


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id"), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    item: Mapped[Item] = relationship(back_populates="comments")
    user: Mapped[Optional["User"]] = relationship(back_populates="comments")


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id"), nullable=False, unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    kind: Mapped[PriceKind] = mapped_column(
        SQLEnum(PriceKind, name="price_kind_enum"),
        default=PriceKind.PURCHASE,
        nullable=False,
    )
    frequency: Mapped[Optional[PriceFrequency]] = mapped_column(
        SQLEnum(PriceFrequency, name="price_frequency_enum"), nullable=True
    )

    item: Mapped[Item] = relationship(back_populates="price")
