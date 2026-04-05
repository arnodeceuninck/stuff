from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schemas import TokenPayload
from dependencies import get_db
from src.domain.models import User

router = APIRouter(prefix="/users", tags=["users"])


class UserProfile(BaseModel):
    id: str
    display_name: str | None
    preferred_currency: str


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
