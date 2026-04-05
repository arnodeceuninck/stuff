from collections.abc import Awaitable, Callable
from functools import lru_cache
from typing import Any, Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from backend_framework.auth.jwt import decode_token
from backend_framework.auth.schemas import RefreshRequest, RegisterRequest, TokenPayload, TokenResponse
from backend_framework.config import FrameworkSettings

AuthEvent = Literal["login", "register", "refresh"]
AuthSuccessHook = Callable[[AuthEvent, TokenPayload], Awaitable[None] | None]


@lru_cache
def get_framework_settings() -> FrameworkSettings:
    return FrameworkSettings()


async def _run_auth_success_hook(
    event: AuthEvent,
    token_response: TokenResponse,
    settings: FrameworkSettings,
    on_auth_success: AuthSuccessHook | None,
) -> None:
    if on_auth_success is None:
        return

    try:
        token_payload = decode_token(token_response.access_token, settings.auth_secret.get_secret_value())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Auth service returned an invalid access token",
        ) from exc

    awaitable = on_auth_success(event, token_payload)
    if awaitable is not None:
        await awaitable


async def _forward_request(
    *,
    settings: FrameworkSettings,
    method: str,
    path: str,
    json_body: dict[str, Any] | None = None,
) -> httpx.Response:
    url = f"{settings.auth_service_url.rstrip('/')}{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            return await client.request(method, url, json=json_body)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Auth service is unavailable",
        ) from exc


def _raise_for_auth_error(response: httpx.Response) -> None:
    if response.status_code < status.HTTP_400_BAD_REQUEST:
        return

    detail: str | dict[str, Any] | list[Any] = "Authentication failed"
    try:
        payload = response.json()
    except ValueError:
        if response.text:
            detail = response.text
    else:
        if isinstance(payload, dict):
            detail = payload.get("detail", payload)
        else:
            detail = payload

    headers = {"WWW-Authenticate": "Bearer"} if response.status_code == 401 else None
    raise HTTPException(status_code=response.status_code, detail=detail, headers=headers)


def _parse_token_response(response: httpx.Response) -> TokenResponse:
    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Auth service returned an invalid response",
        ) from exc

    try:
        return TokenResponse.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Auth service returned an invalid response",
        ) from exc


def create_auth_proxy_router(*, on_auth_success: AuthSuccessHook | None = None) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/login", response_model=TokenResponse)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
        settings = get_framework_settings()
        response = await _forward_request(
            settings=settings,
            method="POST",
            path="/auth/login",
            json_body={
                "email": form_data.username,
                "password": form_data.password,
            },
        )
        _raise_for_auth_error(response)
        token_response = _parse_token_response(response)
        await _run_auth_success_hook("login", token_response, settings, on_auth_success)
        return token_response

    @router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
    async def register(body: RegisterRequest) -> TokenResponse:
        settings = get_framework_settings()
        response = await _forward_request(
            settings=settings,
            method="POST",
            path="/auth/register",
            json_body=body.model_dump(mode="json"),
        )
        _raise_for_auth_error(response)
        token_response = _parse_token_response(response)
        await _run_auth_success_hook("register", token_response, settings, on_auth_success)
        return token_response

    @router.post("/refresh", response_model=TokenResponse)
    async def refresh(body: RefreshRequest) -> TokenResponse:
        settings = get_framework_settings()
        response = await _forward_request(
            settings=settings,
            method="POST",
            path="/auth/refresh",
            json_body=body.model_dump(mode="json"),
        )
        _raise_for_auth_error(response)
        token_response = _parse_token_response(response)
        await _run_auth_success_hook("refresh", token_response, settings, on_auth_success)
        return token_response

    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
    async def logout(body: RefreshRequest) -> Response:
        settings = get_framework_settings()
        response = await _forward_request(
            settings=settings,
            method="POST",
            path="/auth/logout",
            json_body=body.model_dump(mode="json"),
        )
        _raise_for_auth_error(response)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
