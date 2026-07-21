import decimal

from app.commons import event_bus as eb


class WhatsAppMessageRequested(eb.DomainEvent):
    remote_jid: str
    message: str


class TokenRequested(eb.DomainEvent):
    user_id: str
    phone_number: str
    verification_code: str


class TokenVerified(eb.DomainEvent):
    user_id: str
    phone_number: str


class UserCreated(eb.DomainEvent):
    user_id: str


class ApplyMovementRequested(eb.DomainEvent):
    idempotency_key: str
    user_id: str
    amount: decimal.Decimal
    category: str
    description: str
    movement_type: str


class MovementApplied(eb.DomainEvent):
    idempotency_key: str
    user_id: str
    amount: decimal.Decimal
    category: str
    description: str
    movement_type: str


class MovementApplicationFailed(eb.DomainEvent):
    idempotency_key: str
    user_id: str
    error_message: str
