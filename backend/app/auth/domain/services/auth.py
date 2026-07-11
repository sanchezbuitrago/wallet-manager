import datetime
import jwt

from app.auth.domain.model import exceptions, dtos, commands
from app.auth.domain.model import aggregates
from app.commons.adapters import unit_of_work
from app.commons import logs

_LOGGER = logs.get_logger()

_DEFAULT_ACCESS_TOKEN_TIMEDELTA_IN_HOURS = 1
_DEFAULT_REFRESH_TOKEN_TIMEDELTA_IN_HOURS = 24


def _create_access_token(user_id: str, tokens_secret_key: str, algorithm:str) -> str:
    return jwt.encode(
        payload=dtos.TokenInfo(
            user_id=user_id,
            exp=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=_DEFAULT_ACCESS_TOKEN_TIMEDELTA_IN_HOURS),
            token_type=dtos.TokenType.ACCESS_TOKEN,
        ).model_dump(),
        key=tokens_secret_key,
        algorithm=algorithm
    )


def _create_refresh_toke(user_id: str, tokens_secret_key: str, algorithm:str) -> str:
    return jwt.encode(
        payload=dtos.TokenInfo(
            user_id=user_id,
            exp=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=_DEFAULT_REFRESH_TOKEN_TIMEDELTA_IN_HOURS),
            token_type=dtos.TokenType.REFRESH_TOKEN,
        ).model_dump(),
        key=tokens_secret_key,
        algorithm=algorithm
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
        uow: unit_of_work.AbstractUnitOfWork,
        cmd: commands.DoLoginRequest,
        auth_secret_key: str,
        algorithm: str
) -> dtos.LoginResponse:
    _LOGGER.info("Try to do login with email [%s]", cmd.email)
    repo = uow.get_repo(entity_type=aggregates.User)

    user: aggregates.User = next(repo.find_by(find={"email": cmd.email}), None)
    if not user:
        _LOGGER.info("The email [%s] is not registered", cmd.email)
        raise exceptions.EmailNotFoundError()

    if user.pin != cmd.pin:
        _LOGGER.info("Pin not match to do login with email [%s]", cmd.email)
        raise exceptions.PINNotMatchError()

    _LOGGER.info("Login process successfully for email [%s]", cmd.email)

    return dtos.LoginResponse(
        access_token=_create_access_token(user_id=user.id.value, tokens_secret_key=auth_secret_key, algorithm=algorithm),
        refresh_token=_create_refresh_toke(user_id=user.id.value, tokens_secret_key=auth_secret_key, algorithm=algorithm)
    )
