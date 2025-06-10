from app.commons import base_types, standard_types


class UserId(base_types.EntityId):
    id: str


class User(base_types.Aggregate):
    id: UserId
    first_names: str
    last_names: str
    email: str
    phone_number: standard_types.PhoneNumber
    pin: str

    @staticmethod
    def create(first_names: str, last_names: str, email: str, phone_number: standard_types.PhoneNumber, pin: str) -> "User":
        return User(
            id=UserId(id="1234"),
            first_names=first_names,
            last_names=last_names,
            email=email,
            phone_number=phone_number,
            pin=pin
        )