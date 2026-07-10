import pydantic
import random
import string

from typing import Any

from app.commons import base_types


_CHARSET = string.ascii_letters + string.digits


class ApiError(base_types.ValueObject):
    title: str
    code: str
    detail: str


class ApiResponse(base_types.ValueObject):
    success: bool
    body: dict[str, Any]
    errors: list[ApiError]



class PhoneNumber(base_types.ValueObject):
    country_code: str
    number: str

class IdGenerator:

    @staticmethod
    def generate(length: int = 10, uppercase_only: bool = True) -> str:
        id_generated = ''.join(random.choices(_CHARSET, k=length))
        if uppercase_only:
            return id_generated.upper()
        return id_generated