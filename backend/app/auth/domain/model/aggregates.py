import enum
import time

from app.commons import base_types
from app.commons import standard_types


_VERIFICATION_CODE_EXPIRY_SECONDS = 300


class UserId(base_types.EntityId):
    id: str


class UserStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"


class User(base_types.Aggregate):
    """User aggregate owning authentication credentials and profile data."""

    id: UserId
    first_names: str
    last_names: str
    email: str
    phone_number: standard_types.PhoneNumber
    full_phone: str
    pin: str
    status: UserStatus = UserStatus.PENDING
    verification_code: str | None = None
    verification_code_expires_at: float | None = None

    @staticmethod
    def create(
        first_names: str,
        last_names: str,
        email: str,
        phone_number: standard_types.PhoneNumber,
        pin: str,
    ) -> "User":
        """Create a new user with the given profile information."""
        return User(
            id=UserId(id=standard_types.IdGenerator.generate()),
            first_names=first_names,
            last_names=last_names,
            email=email,
            phone_number=phone_number,
            full_phone=f"{phone_number.country_code}{phone_number.number}",
            pin=pin,
            status=UserStatus.PENDING,
        )

    def assign_verification_code(self, code: str) -> None:
        """Assign a verification code with an expiry timestamp."""
        self.verification_code = code
        self.verification_code_expires_at = time.time() + _VERIFICATION_CODE_EXPIRY_SECONDS

    def is_verification_code_valid(self, code: str) -> bool:
        """Check if the provided code matches and has not expired."""
        if self.verification_code != code:
            return False
        if self.verification_code_expires_at is None:
            return False
        return time.time() < self.verification_code_expires_at

    def activate(self) -> None:
        """Set user status to ACTIVE and clear verification data."""
        self.status = UserStatus.ACTIVE
        self.verification_code = None
        self.verification_code_expires_at = None

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE
