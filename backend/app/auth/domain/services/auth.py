import datetime
import jwt

from app.auth.domain.model import exceptions, dtos, commands, aggregates
from app.auth.domain.model.dtos import TokenInfo
from app.commons.adapters import unit_of_work
from app.commons import logs
from app.auth.repository import user as user_repository

_LOGGER = logs.get_logger()

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


def do_login(
        uow: unit_of_work.UnitOfWork,
        cmd: commands.DoLoginRequest,
        auth_secret_key: str
) -> dtos.LoginResponse:
    _LOGGER.info("Try to do login with email [%s]", cmd.email)
    repo: user_repository.FakeUserRepository = uow.get_custom_repository(entity_type=aggregates.User, repository_type=user_repository.FakeUserRepository)
    user: aggregates.User = repo.find_by_email(email=cmd.email)
    if not user:
        _LOGGER.info("The email [%s] is not registered", cmd.email)
        raise exceptions.EmailNotFoundError()

    if user.pin != cmd.pin:
        _LOGGER.info("Pin not mathc to do login with email [%s]", cmd.email)
        raise exceptions.PINNotMatchError()

    _LOGGER.info("Login process successfully for email [%s]", cmd.email)

    return dtos.LoginResponse(
        access_token=_create_access_token(user_id=user.id.value, tokens_secret_key=auth_secret_key),
        refresh_token=_create_refresh_toke(user_id=user.id.value, tokens_secret_key=auth_secret_key)
    )
