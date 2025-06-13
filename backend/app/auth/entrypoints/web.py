import fastapi
import pydantic_settings
from app.commons.adapters import unit_of_work
from app.auth.domain.model import commands, exceptions
from app.commons import standard_types, wrappers, formatters

from app.auth.domain.services import users, auth

auth_routes = fastapi.APIRouter()
users_routes = fastapi.APIRouter()


class _Settings(pydantic_settings.BaseSettings):
    auth_secret_key: str


_SETTINGS = _Settings()


@users_routes.post("/")
async def create_user(create_user_request: commands.CreateUserRequest) -> fastapi.Response:
    try:
        users.create_user(
            uow=unit_of_work.FakeUnitOfWork(),
            cmd=create_user_request
        )
        return fastapi.Response(
            content=formatters.format_response(
                success=True,
                body={},
                errors=[]
            )
        )
    except exceptions.UserAlreadyExistError:
        return fastapi.Response(
            content=formatters.format_response(
                success=False,
                body={},
                errors=[
                    standard_types.ApiError(
                        title="User Already Exist",
                        code="USER_ALREADY_EXIST",
                        detail=f"User with email [{create_user_request.email}] already exist"
                    )
                ]
            )
        )


@auth_routes.post("/login")
async def do_login(create_user_request: commands.DoLoginRequest) -> fastapi.Response:
    try:
        login_response = auth.do_login(
            uow=unit_of_work.FakeUnitOfWork(),
            cmd=create_user_request,
            auth_secret_key=_SETTINGS.auth_secret_key
        )
        return fastapi.Response(
            content=formatters.format_response(
                success=True,
                body=login_response.model_dump(),
                errors=[]
            )
        )
    except (exceptions.EmailNotFoundError, exceptions.PINNotMatchError):
        return fastapi.Response(
            content=formatters.format_response(
                success=False,
                body={},
                errors=[
                    standard_types.ApiError(
                        title="Bad email or password",
                        code="BAD_EMAIL_OR_PASSWORD_ERROR",
                        detail=f"The email or pin are incorrect"
                    )
                ]
            )
        )


@users_routes.patch("/users/pin")
@wrappers.authentication_required
async def change_pin(change_pin_request: commands.ChangePINRequest, authorization: str = fastapi.Header(None)) -> fastapi.Response:
    ...
