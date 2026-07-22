import http
import datetime
import jwt
import functools
from typing import Any, Callable

import fastapi
import pydantic_settings

from app.commons import context
from app.commons import logs
from app.commons import formatters
from app.commons import standard_types
from app.auth.domain.model import dtos

_LOGGER = logs.get_logger()


class _Settings(pydantic_settings.BaseSettings):
    auth_secret_key: str
    algorithm: str


_SETTINGS = _Settings()

_AUTHORIZATION_HEADER_KEY = "authorization"


def authentication_required(function: Callable = None, *, admin_required: bool = False, user_only: bool = False) -> Callable:
    """Decorator that validates a JWT token before executing the endpoint.

    Extracts the Bearer token from the ``authorization`` header, decodes
    it, checks expiry, and stores the user ID in ``UserContext``.
    When ``admin_required`` is True, also verifies the token has is_admin=True.
    When ``user_only`` is True, rejects tokens with is_admin=True.

    Args:
        function: The async endpoint function to protect.
        admin_required: If True, require admin privileges.
        user_only: If True, reject admin tokens (regular users only).

    Returns:
        The wrapped function with JWT validation.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> fastapi.Response:
            _LOGGER.debug("kwargs: %s", kwargs)
            authorization_header = kwargs.get(_AUTHORIZATION_HEADER_KEY)
            _LOGGER.warning("VALIDATING TOKEN ##############################")
            if not authorization_header:
                _LOGGER.warning("Valid token missing")
                return formatters.format_http_response(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    success=False,
                    body={},
                    errors=[
                        standard_types.ApiError(
                            title="User unauthorized",
                            code="AUTH/UNAUTHORIZED",
                            detail="Missing authentication token"
                        )
                    ]
                )
            try:
                _LOGGER.info("Token: %s", authorization_header)
                token = dtos.TokenInfo.model_validate(
                    obj=jwt.decode(
                        authorization_header.split(" ")[-1],
                        key=_SETTINGS.auth_secret_key,
                        algorithms=_SETTINGS.algorithm,
                    )
                )
            except jwt.ExpiredSignatureError:
                _LOGGER.warning("Token has expired")
                return formatters.format_http_response(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    success=False,
                    body={},
                    errors=[
                        standard_types.ApiError(
                            title="User unauthorized",
                            code="AUTH/EXPIRED_TOKEN",
                            detail="Token expired"
                        )
                    ]
                )
            except jwt.DecodeError as e:
                _LOGGER.warning("Token is invalid, Exception: %s", str(e))
                return formatters.format_http_response(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    success=False,
                    body={},
                    errors=[
                        standard_types.ApiError(
                            title="User unauthorized",
                            code="AUTH/UNAUTHORIZED",
                            detail="Invalid token"
                        )
                    ]
                )

            _LOGGER.warning(token.exp)
            _LOGGER.warning(datetime.datetime.now(tz=datetime.UTC).timestamp())
            if token.exp < datetime.datetime.now(tz=datetime.UTC):
                _LOGGER.warning("TOKEN EXPIRED ##############################")
                return formatters.format_http_response(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    success=False,
                    body={},
                    errors=[
                        standard_types.ApiError(
                            title="User unauthorized",
                            code="AUTH/UNAUTHORIZED",
                            detail="Token expired"
                        )
                    ]
                )

            if admin_required and not token.is_admin:
                _LOGGER.warning("User [%s] is not admin", token.user_id)
                return formatters.format_http_response(
                    status_code=http.HTTPStatus.FORBIDDEN,
                    success=False,
                    body={},
                    errors=[
                        standard_types.ApiError(
                            title="Forbidden",
                            code="NOT_ADMIN",
                            detail="Admin privileges required"
                        )
                    ]
                )

            if user_only and token.is_admin:
                _LOGGER.warning("Admin token not allowed for user-only endpoint [%s]", token.user_id)
                return formatters.format_http_response(
                    status_code=http.HTTPStatus.FORBIDDEN,
                    success=False,
                    body={},
                    errors=[
                        standard_types.ApiError(
                            title="Forbidden",
                            code="ADMIN_NOT_ALLOWED",
                            detail="Admin tokens not allowed for this endpoint"
                        )
                    ]
                )

            context.UserContext.set(user_id=token.user_id)
            return await func(*args, **kwargs)

        return wrapper

    if function is not None:
        return decorator(function)
    return decorator
