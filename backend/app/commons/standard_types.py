import pydantic
import random
import string
import time

from typing import Any

from app.commons import base_types


_CHARSET = string.ascii_letters + string.digits


class Timestamp(pydantic.BaseModel):
    """Unix timestamp value object with comparison and formatting helpers."""

    value: float

    @staticmethod
    def now() -> "Timestamp":
        """Create a Timestamp representing the current moment."""
        return Timestamp(value=time.time())

    def as_seconds(self) -> float:
        """Return the raw timestamp value in seconds."""
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
        """Return seconds elapsed since this timestamp."""
        return time.time() - self.value

    def to_utc_string(self) -> str:
        """Return an ISO-8601 UTC string representation."""
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.value))

    def format_timestamp(self, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str:
        """Format the timestamp using a strftime format string.

        Args:
            fmt: A strftime-compatible format string.

        Returns:
            The formatted timestamp string.
        """
        return time.strftime(fmt, time.gmtime(self.value))

    @staticmethod
    def from_string(s: str) -> "Timestamp":
        """Parse a timestamp from a numeric string or ISO-8601 format."""
        try:
            return Timestamp(value=float(s))
        except ValueError:
            import datetime
            dt = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
            return Timestamp(value=dt.timestamp())


class ApiError(base_types.ValueObject):
    """Standard error object included in API responses."""

    title: str
    code: str
    detail: str


class ApiResponse(base_types.ValueObject):
    """Standard envelope for all API responses."""

    success: bool
    body: dict[str, Any]
    errors: list[ApiError]


class PhoneNumber(base_types.ValueObject):
    """Phone number split into country code and local number."""

    country_code: str
    number: str


class IdGenerator:
    """Utility for generating random alphanumeric IDs."""

    @staticmethod
    def generate(length: int = 10, uppercase_only: bool = True) -> str:
        """Generate a random ID string.

        Args:
            length: Number of characters in the ID.
            uppercase_only: If True, return only uppercase letters.

        Returns:
            A random alphanumeric string.
        """
        id_generated = ''.join(random.choices(_CHARSET, k=length))
        if uppercase_only:
            return id_generated.upper()
        return id_generated
