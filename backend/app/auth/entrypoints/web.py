import http

import fastapi
import pydantic_settings

from app.commons import context
from app.commons import logs
from app.commons.adapters import mongo_uow
from app.auth.domain.model import commands
from app.auth.domain.model import exceptions
from app.commons import standard_types
from app.commons import wrappers
from app.commons import formatters

from app.auth.domain.services import users
from app.auth.domain.services import auth
import pydantic

_LOGGER = logs.get_logger()

auth_routes = fastapi.APIRouter()
users_routes = fastapi.APIRouter()


class RefreshTokenRequest(pydantic.BaseModel):
    """Request body for the token refresh endpoint."""

    refresh_token: str


class _Settings(pydantic_settings.BaseSettings):
    auth_secret_key: str
    algorithm: str


_SETTINGS = _Settings()


@users_routes.post("/")
async def create_user(
    create_user_request: commands.CreateUserRequest,
) -> fastapi.Response:
    """Register a new user account or update a pending one."""
    try:
        users.create_user(
            uow=mongo_uow.MongoUOW(),
            cmd=create_user_request
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except exceptions.UserAlreadyExistError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="User Already Exist",
                    code="USER_ALREADY_EXIST",
                    detail=f"User with email [{create_user_request.email}] already exist and is active"
                )
            ]
        )
    except exceptions.PhoneNumberAlreadyExistError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Phone Number Already In Use",
                    code="PHONE_NUMBER_ALREADY_EXIST",
                    detail="El numero de telefono ya esta registrado por otro usuario"
                )
            ]
        )


@users_routes.post("/verify")
async def verify_token(
    body: commands.VerifyTokenRequest,
) -> fastapi.Response:
    """Verify a user's verification code and activate their account."""
    try:
        users.verify_token(
            uow=mongo_uow.MongoUOW(),
            cmd=body,
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except exceptions.EmailNotFoundError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="User Not Found",
                    code="USER_NOT_FOUND",
                    detail=f"No user found with email [{body.email}]"
                )
            ]
        )
    except exceptions.InvalidVerificationCodeError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Invalid Code",
                    code="INVALID_VERIFICATION_CODE",
                    detail="The verification code is incorrect"
                )
            ]
        )
    except exceptions.VerificationCodeExpiredError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Code Expired",
                    code="VERIFICATION_CODE_EXPIRED",
                    detail="The verification code has expired. Please request a new one."
                )
            ]
        )


@auth_routes.post("/login")
async def do_login(
    create_user_request: commands.DoLoginRequest,
) -> fastapi.Response:
    """Authenticate and return JWT tokens."""
    try:
        login_response = auth.do_login(
            uow=mongo_uow.MongoUOW(),
            cmd=create_user_request,
            auth_secret_key=_SETTINGS.auth_secret_key,
            algorithm=_SETTINGS.algorithm
        )
        return formatters.format_http_response(
            success=True,
            body=login_response.model_dump(),
            errors=[]
        )
    except exceptions.EmailNotFoundError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Bad email or password",
                    code="BAD_EMAIL_OR_PASSWORD_ERROR",
                    detail="The email or pin are incorrect"
                )
            ]
        )
    except exceptions.PinNotMatchError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Bad email or password",
                    code="BAD_EMAIL_OR_PASSWORD_ERROR",
                    detail="The email or pin are incorrect"
                )
            ]
        )
    except exceptions.UserNotActiveError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Account Not Active",
                    code="USER_NOT_ACTIVE",
                    detail="Tu cuenta esta pendiente de verificacion. Por favor verifica tu numero de telefono."
                )
            ]
        )


@auth_routes.post("/refresh")
async def refresh_token(
    body: RefreshTokenRequest,
) -> fastapi.Response:
    """Issue a new access token using a valid refresh token."""
    try:
        login_response = auth.do_refresh(
            refresh_token=body.refresh_token,
            auth_secret_key=_SETTINGS.auth_secret_key,
            algorithm=_SETTINGS.algorithm,
        )
        return formatters.format_http_response(
            success=True,
            body=login_response.model_dump(),
            errors=[]
        )
    except (
        exceptions.AccessTokenNotValidError,
        exceptions.RefreshTokenExpiredError,
        exceptions.TokenTypeNotValidError,
    ):
        return formatters.format_http_response(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Invalid refresh token",
                    code="AUTH/INVALID_REFRESH_TOKEN",
                    detail="The refresh token is invalid or has expired"
                )
            ]
        )


@users_routes.get("/myself")
@wrappers.authentication_required
async def get_myself(
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Get the authenticated user's profile."""
    try:
        user_id = context.UserContext.get()
        user = users.get_myself(
            user_id=user_id,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={
                "id": user.id.value,
                "first_names": user.first_names,
                "last_names": user.last_names,
                "email": user.email,
                "phone_number": user.phone_number.model_dump(),
                "full_phone": user.full_phone,
                "status": user.status.value,
            },
            errors=[]
        )
    except exceptions.EmailNotFoundError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="User Not Found",
                    code="USER_NOT_FOUND",
                    detail="User not found"
                )
            ]
        )


@users_routes.patch("/myself/profile")
@wrappers.authentication_required
async def request_profile_update(
    body: commands.UpdateProfileRequest,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Stage profile changes and send a verification code."""
    try:
        user_id = context.UserContext.get()
        requires_verification = users.request_profile_update(
            cmd=body,
            user_id=user_id,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={"requires_verification": requires_verification},
            errors=[]
        )
    except exceptions.UserAlreadyExistError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Email Already In Use",
                    code="USER_ALREADY_EXIST",
                    detail="The email is already registered by another user"
                )
            ]
        )
    except exceptions.PhoneNumberAlreadyExistError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Phone Number Already In Use",
                    code="PHONE_NUMBER_ALREADY_EXIST",
                    detail="The phone number is already registered by another user"
                )
            ]
        )


@users_routes.post("/myself/verify")
@wrappers.authentication_required
async def verify_profile_update(
    body: commands.VerifyTokenRequest,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Verify the code and apply staged profile changes."""
    try:
        user_id = context.UserContext.get()
        users.verify_profile_update(
            cmd=body,
            user_id=user_id,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except exceptions.InvalidVerificationCodeError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Invalid Code",
                    code="INVALID_VERIFICATION_CODE",
                    detail="The verification code is incorrect"
                )
            ]
        )
    except exceptions.VerificationCodeExpiredError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Code Expired",
                    code="VERIFICATION_CODE_EXPIRED",
                    detail="The verification code has expired. Please request a new one."
                )
            ]
        )


@users_routes.patch("/myself/pin")
@wrappers.authentication_required
async def change_pin(
    change_pin_request: commands.ChangePinRequest,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Validate current PIN, stage new PIN, and send a verification code."""
    try:
        user_id = context.UserContext.get()
        users.change_pin(
            cmd=change_pin_request,
            user_id=user_id,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except exceptions.EmailNotFoundError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="User Not Found",
                    code="USER_NOT_FOUND",
                    detail="User not found"
                )
            ]
        )
    except exceptions.PinNotMatchError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Invalid PIN",
                    code="PIN_NOT_MATCH",
                    detail="The current PIN is incorrect"
                )
            ]
        )


@auth_routes.post("/pin-recovery")
async def request_pin_recovery(
    body: commands.RequestPinRecoveryRequest,
) -> fastapi.Response:
    """Send a verification code to the user's phone for PIN recovery."""
    try:
        users.request_pin_recovery(
            cmd=body,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except exceptions.EmailNotFoundError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="User Not Found",
                    code="USER_NOT_FOUND",
                    detail=f"No user found with email [{body.email}]"
                )
            ]
        )
    except exceptions.UserNotActiveError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Account Not Active",
                    code="USER_NOT_ACTIVE",
                    detail="Tu cuenta esta pendiente de verificacion. Por favor verifica tu numero de telefono."
                )
            ]
        )


@auth_routes.post("/pin-recovery/verify")
async def reset_pin(
    body: commands.ResetPinRequest,
) -> fastapi.Response:
    """Verify recovery code and set a new PIN."""
    try:
        code_expired = users.reset_pin(
            cmd=body,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={"code_expired": code_expired},
            errors=[]
        )
    except exceptions.EmailNotFoundError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="User Not Found",
                    code="USER_NOT_FOUND",
                    detail=f"No user found with email [{body.email}]"
                )
            ]
        )
    except exceptions.UserNotActiveError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Account Not Active",
                    code="USER_NOT_ACTIVE",
                    detail="Tu cuenta esta pendiente de verificacion. Por favor verifica tu numero de telefono."
                )
            ]
        )
    except exceptions.InvalidVerificationCodeError:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Invalid Code",
                    code="INVALID_VERIFICATION_CODE",
                    detail="The verification code is incorrect"
                )
            ]
        )
