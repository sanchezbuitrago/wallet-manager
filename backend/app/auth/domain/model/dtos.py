import datetime
import enum

from app.commons import base_types


class TokenType(enum.StrEnum):
    ACCESS_TOKEN = "ACCESS_TOKEN"
    REFRESH_TOKEN = "REFRESH_TOKEN"


class TokenInfo(base_types.ValueObject):
    user_id: str
    exp: datetime.datetime
    token_type: TokenType
