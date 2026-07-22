from app.commons import base_types
from app.commons import standard_types


class CreateUserRequest(base_types.ValueObject):
    first_names: str
    last_names: str
    email: str
    phone_number: standard_types.PhoneNumber
    pin: str


class DoLoginRequest(base_types.ValueObject):
    email: str
    pin: str
    require_admin: bool = False


class ChangePinRequest(base_types.ValueObject):
    old_pin: str
    new_pin: str


class VerifyTokenRequest(base_types.ValueObject):
    email: str
    code: str


class UpdateProfileRequest(base_types.ValueObject):
    first_names: str | None = None
    last_names: str | None = None
    email: str | None = None
    phone_number: standard_types.PhoneNumber | None = None
    pin: str | None = None


class RequestPinRecoveryRequest(base_types.ValueObject):
    email: str


class ResetPinRequest(base_types.ValueObject):
    email: str
    code: str
    new_pin: str
