import datetime

import pydantic

from app.commons import base_types, standard_types


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
