import enum


from app.commons import base_types

class MediaFile(base_types.ValueObject):
    media_type: str
    file_name: str
    mime_type: str
    base_64: str


class MessageType(enum.StrEnum):
    AUDIO = "AUDIO"
    TEXT = "TEXT"


class N8NMediaFile(base_types.ValueObject):
    type: MessageType
    number: str
    user_id: str
    media_file: MediaFile