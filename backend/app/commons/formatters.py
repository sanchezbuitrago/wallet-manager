import json
from typing import Dict, Any, List
from app.commons import standard_types


def format_response(success: bool, body: Dict[str, Any], errors: List[standard_types.ApiError]) -> str:
    return json.dumps(obj=standard_types.ApiResponse(
        success=success,
        body=body,
        errors=errors
    ).model_dump())
