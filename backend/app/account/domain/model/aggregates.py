import decimal
from app.commons import base_types
from app.commons import standard_types


class MovementId(base_types.EntityId):
    id: str


class Movement(base_types.Aggregate):
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

    @staticmethod
    def create(
        account_id: str,
        user_id: str,
        money: base_types.Money,
        opening_balance: base_types.Money,
        closing_balance: base_types.Money,
        category: str,
        description: str,
        movement_type: str
    ) -> "Movement":
        return Movement(
            id=MovementId(id=standard_types.IdGenerator.generate()),
            account_id=account_id,
            user_id=user_id,
            money=money,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            category=category,
            description=description,
            movement_type=movement_type,
            created_at=standard_types.Timestamp.now()
        )


class AccountId(base_types.EntityId):
    id: str


class Account(base_types.Aggregate):
    id: AccountId
    user_id: str
    balance: base_types.Money
    created_at: standard_types.Timestamp
    updated_at: standard_types.Timestamp

    @staticmethod
    def create(user_id: str) -> "Account":
        now = standard_types.Timestamp.now()
        return Account(
            id=AccountId(id=standard_types.IdGenerator.generate()),
            user_id=user_id,
            balance=base_types.Money(amount=decimal.Decimal("0")),
            created_at=now,
            updated_at=now,
        )

    def credit(self, amount: decimal.Decimal) -> None:
        self.balance.amount += amount
        self.updated_at = standard_types.Timestamp.now()

    def debit(self, amount: decimal.Decimal) -> None:
        self.balance.amount -= amount
        self.updated_at = standard_types.Timestamp.now()
