from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError  # noqa: F401 — re-exported for callers

from auth.schemas import TokenPayload


def create_access_token(user_id: str, email: str, secret: str, expires_minutes: int = 60) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(
        {"sub": user_id, "email": email, "exp": expire},
        secret,
        algorithm="HS256",
    )


def decode_token(token: str, secret: str) -> TokenPayload:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    return TokenPayload(sub=payload["sub"], email=payload["email"])
