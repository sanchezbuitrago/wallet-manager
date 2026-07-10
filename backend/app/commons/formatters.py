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
