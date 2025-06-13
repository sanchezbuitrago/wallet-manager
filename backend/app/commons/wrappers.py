import http
import datetime
import jwt
from functools import wraps
from typing import Callable, Any

from app.commons import logs, formatters
from app.commons import standard_types

from fastapi import Response

_LOGGER = logs.get_logger()

_AUTHORIZATION_HEADER_KEY = "authorization"


def authentication_required(function: Callable) -> Callable:
    @wraps(function)
    def decorator(*args: Any, **kwargs: Any) -> Response:
        print(kwargs)
        authorization_header = kwargs.get(_AUTHORIZATION_HEADER_KEY)
        _LOGGER.warning("VALIDATING TOKEN ##############################")
        if not authorization_header:
            _LOGGER.warning("Valid token missing")
            return Response(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                content=formatters.format_response(
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
            )
        try:
            data = jwt.decode(authorization_header.split(" ")[-1], verify=False)
        except jwt.DecodeError as e:
            _LOGGER.warning("Token is invalid, Exception: %s", str(e))
            return Response(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                content=formatters.format_response(
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
            )

        _LOGGER.warning(data["exp"])
        _LOGGER.warning(datetime.datetime.now(tz=datetime.UTC).timestamp())
        if data["exp"] < datetime.datetime.now(tz=datetime.UTC).timestamp():
            _LOGGER.warning("TOKEN EXPIRED ##############################")
            return Response(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                content=formatters.format_response(
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
            )
        return function(*args, **kwargs)

    return decorator