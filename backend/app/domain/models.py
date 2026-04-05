from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


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


class Price(BaseModel):
    amount: Decimal
    currency: str = "EUR"
    kind: PriceKind = PriceKind.PURCHASE
    frequency: Optional[PriceFrequency] = None

class Merchant(BaseModel):
    id: str # uuid
    name: str
    website: Optional[str] = None
    note: Optional[str] = None

class User(BaseModel):
    id: str # uuid
    email: Optional[str] = None

class Attachement(BaseModel):
    id: str # uuid
    filename: str
    url: str
    upload_date: Optional[str] = None

class Comment(BaseModel):
    id: str # uuid
    item_id: str
    user_id: Optional[str] = None
    content: str
    created_at: Optional[str] = None

class Item(BaseModel):
    id: str # uuid

    # Item info
    name: str
    attachments: List[Attachement] = []
    primary_image: Optional[Attachement] = None # uuid of the attachment that is the primary image
    description: Optional[str] = None
    comments: List[Comment] = []
    
    user_id: Optional[str] = None

    location_id: Optional[str] = None
    
    ownership_type: Optional[str] = "OWNED" # OWNED, RENTED, BORROWED, WANTED, NEEDED
    
    linked_location_id: Optional[str] = None # If the item itself is a location (e.g. a wardrobe)
    
    # Purchase details
    price: Optional[Price] = None
    purchased_date: Optional[str] = None
    merchant_id: Optional[str] = None

class Location(BaseModel):
    id: str # uuid
    name: str
    parent_location_id: Optional[str] = None
    note: Optional[str] = None
    items: List[Item] = []
