import pydantic

from app.commons import base_types

class DataKeyEvent(base_types.ValueObject):
    id: str
    remote_jid: str = pydantic.Field(alias="remoteJid")
    from_me: bool = pydantic.Field(alias="fromMe")

class AudioMessage(base_types.ValueObject):
    url: str

class WhatsappEventMessage(base_types.ValueObject):
    conversation: str | None = None
    audio_message: AudioMessage | None = pydantic.Field(alias="audioMessage", default=None)


class DataEvent(base_types.ValueObject):
    key: DataKeyEvent
    message: WhatsappEventMessage

class WhatsappEventCommand(base_types.ValueObject):
    event: str
    instance: str
    data: DataEvent
    sender: str


import decimal

class MovementPayload(base_types.ValueObject):
    amount: decimal.Decimal
    category: str = ""
    description: str = ""
    movement_type: str = ""