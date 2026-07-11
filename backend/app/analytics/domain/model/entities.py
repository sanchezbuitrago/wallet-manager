from app.commons import base_types, standard_types


class MovementId(base_types.EntityId):
    id: str


class Movement(base_types.ForeignAggregate):
    id: MovementId
    account_id: str
    user_id: str
    money: base_types.Money
    opening_balance: base_types.Money
    closing_balance: base_types.Money
    category: str
    description: str
    movement_type: str
    created_at: standard_types.Timestamp


class AccountId(base_types.EntityId):
    id: str


class Account(base_types.ForeignAggregate):
    id: AccountId
    user_id: str
    balance: base_types.Money
    created_at: standard_types.Timestamp
    updated_at: standard_types.Timestamp
