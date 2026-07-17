from app.commons import base_types
from app.commons import standard_types


class UserId(base_types.EntityId):
    id: str


class User(base_types.Aggregate):
    """User aggregate owning authentication credentials and profile data."""

    id: UserId
    first_names: str
    last_names: str
    email: str
    phone_number: standard_types.PhoneNumber
    full_phone: str
    pin: str

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
            pin=pin
        )
