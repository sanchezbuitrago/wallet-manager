import pydantic

from typing import Dict, Any, List

from app.commons import base_types


class ApiError(base_types.ValueObject):
    title: str
    code: str
    detail: str


class ApiResponse(base_types.ValueObject):
    success: bool
    body: Dict[str, Any]
    errors: List[ApiError]



class PhoneNumber(base_types.ValueObject):
    country_code: str
    number: str