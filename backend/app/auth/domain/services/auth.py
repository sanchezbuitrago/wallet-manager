import datetime
import jwt

from app.auth.domain.model import exceptions, dtos
from app.auth.domain.model.dtos import TokenInfo

_DEFAULT_ACCESS_TOKEN_TIMEDELTA_IN_HOURS = 1
_DEFAULT_REFRESH_TOKEN_TIMEDELTA_IN_HOURS = 24


def _create_access_token(user_id: str, tokens_secret_key: str) -> str:
    return jwt.encode(
        TokenInfo(
            user_id=user_id,
            exp=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=_DEFAULT_ACCESS_TOKEN_TIMEDELTA_IN_HOURS),
            token_type=dtos.TokenType.ACCESS_TOKEN,
        ).model_dump(),
        tokens_secret_key,
    )


def _create_refresh_toke(user_id: str, tokens_secret_key: str) -> str:
    return jwt.encode(
        TokenInfo(
            user_id=user_id,
            exp=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=_DEFAULT_REFRESH_TOKEN_TIMEDELTA_IN_HOURS),
            token_type=dtos.TokenType.REFRESH_TOKEN,
        ).model_dump(),
        tokens_secret_key,
    )


def _validate_token(access_token: str, token_type: dtos.TokenType) -> None:
    try:
        token_data = jwt.decode(access_token, verify=False)
    except jwt.DecodeError:
        raise exceptions.AccessTokenNotValidError()

    if token_data["exp"] < datetime.datetime.now(tz=datetime.UTC).timestamp():
        raise exceptions.RefreshTokenExpiredError()

    if token_data["token_type"] != token_type:
        raise exceptions.TokenTypeNotValidError()
