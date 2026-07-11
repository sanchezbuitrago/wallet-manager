import datetime
import decimal

from app.commons import base_types, standard_types


class MovementId(base_types.EntityId):
    id: str


class Movement(base_types.Aggregate):
    id: MovementId
    account_id: str
    user_id: str
    money: base_types.Money
    category: str
    description: str
    movement_type: str
    created_at: str

    @staticmethod
    def create(account_id: str, user_id: str, money: base_types.Money,
               category: str, description: str, movement_type: str) -> "Movement":
        return Movement(
            id=MovementId(id=standard_types.IdGenerator.generate()),
            account_id=account_id,
            user_id=user_id,
            money=money,
            category=category,
            description=description,
            movement_type=movement_type,
            created_at=datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        )


class AccountId(base_types.EntityId):
    id: str


class Account(base_types.Aggregate):
    id: AccountId
    user_id: str
    balance: base_types.Money

    @staticmethod
    def create(user_id: str) -> "Account":
        return Account(
            id=AccountId(id=standard_types.IdGenerator.generate()),
            user_id=user_id,
            balance=base_types.Money(amount=decimal.Decimal("0"))
        )

    def credit(self, amount: decimal.Decimal) -> None:
        self.balance.amount += amount

    def debit(self, amount: decimal.Decimal) -> None:
        self.balance.amount -= amount


class ProcessingResult(base_types.ValueObject):
    success: bool
    money: base_types.Money | None = None
    category: str | None = None
    description: str | None = None
    movement_type: str | None = None
    error_message: str = ""


class MessageId(base_types.EntityId):
    id: str


class Message(base_types.Aggregate):
    id: MessageId
    user_id: str
    phone_number: str
    remote_jid: str
    content: str
    message_type: str
    media_url: str | None = None
    processing_result: ProcessingResult | None = None
    created_at: str

    @staticmethod
    def create(user_id: str, phone_number: str, remote_jid: str, content: str,
               message_type: str, media_url: str | None = None) -> "Message":
        return Message(
            id=MessageId(id=standard_types.IdGenerator.generate()),
            user_id=user_id,
            phone_number=phone_number,
            remote_jid=remote_jid,
            content=content,
            message_type=message_type,
            media_url=media_url,
            created_at=datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        )
