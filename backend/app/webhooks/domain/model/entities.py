from app.commons import base_types


class UserId(base_types.EntityId):
    id: str


class User(base_types.ForeignAggregate):
    """Reference to a User owned by the auth context.
    Only contains the ID — lifecycle managed by auth."""
    id: UserId
