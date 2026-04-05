from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from auth.jwt import decode_token
from auth.schemas import TokenPayload
from config import FrameworkSettings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@lru_cache
def _get_settings() -> FrameworkSettings:
    return FrameworkSettings()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    try:
        return decode_token(token, _get_settings().auth_secret)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
