import decimal
from app.commons import base_types


class ProcessMovementCommand(base_types.ValueObject):
    idempotency_key: str
    user_id: str
    amount: decimal.Decimal
    category: str
    description: str
    movement_type: str
