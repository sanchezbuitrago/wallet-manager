import pydantic
import random
import string
import time

from typing import Any

from app.commons import base_types


_CHARSET = string.ascii_letters + string.digits


class Timestamp(pydantic.BaseModel):
    value: float

    @staticmethod
    def now() -> "Timestamp":
        return Timestamp(value=time.time())

    def as_seconds(self) -> float:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"Timestamp({self.value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Timestamp):
            return self.value == other.value
        return NotImplemented

    def __lt__(self, other: "Timestamp") -> bool:
        return self.value < other.value

    def __le__(self, other: "Timestamp") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "Timestamp") -> bool:
        return self.value > other.value

    def __ge__(self, other: "Timestamp") -> bool:
        return self.value >= other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def elapsed(self) -> float:
        return time.time() - self.value

    def to_utc_string(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.value))

    def format(self, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str:
        return time.strftime(fmt, time.gmtime(self.value))

    @staticmethod
    def from_string(s: str) -> "Timestamp":
        try:
            return Timestamp(value=float(s))
        except ValueError:
            import datetime
            dt = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
            return Timestamp(value=dt.timestamp())


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