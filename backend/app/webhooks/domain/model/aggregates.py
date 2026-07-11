import datetime

from app.commons import base_types, standard_types


class MessageId(base_types.EntityId):
    id: str


class Message(base_types.Aggregate):
    id: MessageId
    user_id: str
    phone_number: str
    content: str
    message_type: str
    media_url: str | None = None
    created_at: str

    @staticmethod
    def create(user_id: str, phone_number: str, content: str,
               message_type: str, media_url: str | None = None) -> "Message":
        return Message(
            id=MessageId(id=standard_types.IdGenerator.generate()),
            user_id=user_id,
            phone_number=phone_number,
            content=content,
            message_type=message_type,
            media_url=media_url,
            created_at=datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        )
