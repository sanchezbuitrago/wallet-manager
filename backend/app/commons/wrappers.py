import http
import datetime
import jwt
from functools import wraps
from typing import Callable, Any

import pydantic_settings

from app.commons import context
from app.commons import logs, formatters
from app.commons import standard_types
from app.auth.domain.model import dtos

from fastapi import Response

_LOGGER = logs.get_logger()

class _Settings(pydantic_settings.BaseSettings):
    auth_secret_key: str
    algorithm: str

_SETTINGS = _Settings()

_AUTHORIZATION_HEADER_KEY = "authorization"


def authentication_required(function: Callable) -> Callable:
    @wraps(function)
    async def decorator(*args: Any, **kwargs: Any) -> Response:
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
            token = dtos.TokenInfo.model_validate(obj=jwt.decode(authorization_header.split(" ")[-1], key=_SETTINGS.auth_secret_key, algorithms=_SETTINGS.algorithm))
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
        context.UserContext.set(user_id=token.user_id)
        return await function(*args, **kwargs)

    return decorator