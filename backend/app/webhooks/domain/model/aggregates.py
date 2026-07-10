from datetime import datetime, timezone

from app.commons import base_types, standard_types


class MessageId(base_types.EntityId):
    id: str


class Message(base_types.Aggregate):
    id: MessageId
    user_id: str
    phone_number: str
    content: str
    message_type: str
    created_at: str

    @staticmethod
    def create(user_id: str, phone_number: str, content: str, message_type: str) -> "Message":
        return Message(
            id=MessageId(id=standard_types.IdGenerator.generate()),
            user_id=user_id,
            phone_number=phone_number,
            content=content,
            message_type=message_type,
            created_at=datetime.now(tz=timezone.utc).isoformat()
        )
