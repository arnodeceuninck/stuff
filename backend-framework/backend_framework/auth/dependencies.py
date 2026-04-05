from functools import lru_cache
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from backend_framework.auth.jwt import decode_token
from backend_framework.auth.schemas import TokenPayload
from backend_framework.config import FrameworkSettings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@lru_cache
def _get_settings() -> FrameworkSettings:
    return FrameworkSettings()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    try:
        return decode_token(token, _get_settings().auth_secret.get_secret_value())
    except InvalidTokenError:
        logging.getLogger("backend_framework.auth").warning("Invalid bearer token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )