import datetime
import jwt

import time

from app.auth.domain.model import exceptions
from app.auth.domain.model import dtos
from app.auth.domain.model import commands
from app.auth.domain.model import aggregates
from app.commons.adapters import unit_of_work
from app.commons import logs

_LOGGER = logs.get_logger()

_DEFAULT_ACCESS_TOKEN_TIMEDELTA_IN_HOURS = 1
_DEFAULT_REFRESH_TOKEN_TIMEDELTA_IN_HOURS = 24


def _create_access_token(
    user_id: str,
    tokens_secret_key: str,
    algorithm: str,
    is_admin: bool = False,
) -> str:
    return jwt.encode(
        payload=dtos.TokenInfo(
            user_id=user_id,
            exp=(
                datetime.datetime.now(tz=datetime.UTC)
                + datetime.timedelta(hours=_DEFAULT_ACCESS_TOKEN_TIMEDELTA_IN_HOURS)
            ),
            token_type=dtos.TokenType.ACCESS_TOKEN,
            is_admin=is_admin,
        ).model_dump(),
        key=tokens_secret_key,
        algorithm=algorithm
    )


def _create_refresh_token(
    user_id: str,
    tokens_secret_key: str,
    algorithm: str,
) -> str:
    return jwt.encode(
        payload=dtos.TokenInfo(
            user_id=user_id,
            exp=(
                datetime.datetime.now(tz=datetime.UTC)
                + datetime.timedelta(hours=_DEFAULT_REFRESH_TOKEN_TIMEDELTA_IN_HOURS)
            ),
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


def do_refresh(
        refresh_token: str,
        auth_secret_key: str,
        algorithm: str,
) -> dtos.LoginResponse:
    """Issue a new access token using a valid refresh token.

    Args:
        refresh_token: The refresh token JWT string.
        auth_secret_key: Secret key for JWT signing.
        algorithm: JWT signing algorithm.

    Returns:
        A LoginResponse with a new access token and the same refresh token.

    Raises:
        AccessTokenNotValidError: If the token cannot be decoded.
        RefreshTokenExpiredError: If the refresh token has expired.
        TokenTypeNotValidError: If the token is not a refresh token.
    """
    _LOGGER.info("Trying to refresh access token")
    _validate_token(refresh_token, dtos.TokenType.REFRESH_TOKEN)

    token_data = jwt.decode(
        refresh_token,
        key=auth_secret_key,
        algorithms=algorithm,
    )
    user_id = token_data["user_id"]

    _LOGGER.info("Refresh token valid for user [%s]", user_id)

    return dtos.LoginResponse(
        access_token=_create_access_token(
            user_id=user_id,
            tokens_secret_key=auth_secret_key,
            algorithm=algorithm,
        ),
        refresh_token=refresh_token,
    )


def do_login(
        uow: unit_of_work.AbstractUnitOfWork,
        cmd: commands.DoLoginRequest,
        auth_secret_key: str,
        algorithm: str
) -> dtos.LoginResponse:
    """Authenticate a user by email and PIN.

    Args:
        uow: Unit of work for data access.
        cmd: Login request containing email and PIN.
        auth_secret_key: Secret key for JWT signing.
        algorithm: JWT signing algorithm.

    Returns:
        A LoginResponse with access and refresh tokens.

    Raises:
        EmailNotFoundError: If the email is not registered.
        PinNotMatchError: If the PIN does not match.
    """
    _LOGGER.info("Try to do login with email [%s]", cmd.email)
    repo = uow.get_repo(entity_type=aggregates.User)

    user: aggregates.User = next(repo.find_by(find={"email": cmd.email}), None)
    if not user:
        _LOGGER.info("The email [%s] is not registered", cmd.email)
        raise exceptions.EmailNotFoundError()

    if user.is_blocked:
        _LOGGER.info("User with email [%s] is blocked", cmd.email)
        raise exceptions.UserBlockedError()

    if not user.is_active:
        _LOGGER.info("User with email [%s] is not active", cmd.email)
        raise exceptions.UserNotActiveError()

    if user.pin != cmd.pin:
        _LOGGER.info("Pin not match to do login with email [%s]", cmd.email)
        raise exceptions.PinNotMatchError()

    if cmd.require_admin and not user.is_admin:
        _LOGGER.info("User [%s] is not admin", cmd.email)
        raise exceptions.NotAdminError()

    user.last_login = time.time()
    repo.save(new_item=user)

    _LOGGER.info("Login process successfully for email [%s]", cmd.email)

    return dtos.LoginResponse(
        access_token=_create_access_token(
            user_id=user.id.value,
            tokens_secret_key=auth_secret_key,
            algorithm=algorithm,
            is_admin=user.is_admin,
        ),
        refresh_token=_create_refresh_token(
            user_id=user.id.value,
            tokens_secret_key=auth_secret_key,
            algorithm=algorithm,
        )
    )
