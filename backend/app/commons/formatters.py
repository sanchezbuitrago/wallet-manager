import http
import json
import fastapi
from typing import Any
from app.commons import standard_types


def format_http_response(
        success: bool,
        body: dict[str, Any],
        errors: list[standard_types.ApiError],
        status_code: int = http.HTTPStatus.OK
) -> fastapi.Response:
    """Build a standardized JSON response envelope.

    Args:
        success: Whether the request succeeded.
        body: The response payload.
        errors: List of errors, empty when successful.
        status_code: HTTP status code (defaults to 200).

    Returns:
        A FastAPI Response with JSON content type.
    """
    return fastapi.Response(
        status_code=status_code,
        content=json.dumps(
            obj=standard_types.ApiResponse(
                success=success,
                body=body,
                errors=errors
            ).model_dump()
        ),
        headers={
            "Content-Type": "application/json"
        }
    )
