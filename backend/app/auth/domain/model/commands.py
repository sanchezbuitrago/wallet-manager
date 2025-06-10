from app.commons import base_types, standard_types


class CreateUserRequest(base_types.ValueObject):
    first_names: str
    last_names: str
    email: str
    phone_number: standard_types.PhoneNumber
    pin: str