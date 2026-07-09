import http

import fastapi
import pydantic_settings
from app.commons import context
from app.commons.adapters import mongo_uow
from app.auth.domain.model import commands, exceptions
from app.commons import standard_types, wrappers, formatters

from app.auth.domain.services import users, auth

auth_routes = fastapi.APIRouter()
users_routes = fastapi.APIRouter()


class _Settings(pydantic_settings.BaseSettings):
    auth_secret_key: str
    algorithm: str


_SETTINGS = _Settings()


@users_routes.post("/")
async def create_user(create_user_request: commands.CreateUserRequest) -> fastapi.Response:
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
                    detail=f"User with email [{create_user_request.email}] already exist"
                )
            ]
        )


@auth_routes.post("/login")
async def do_login(create_user_request: commands.DoLoginRequest) -> fastapi.Response:
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
    except (exceptions.EmailNotFoundError, exceptions.PINNotMatchError):
        return formatters.format_http_response(
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


@users_routes.patch("/pin")
@wrappers.authentication_required
async def change_pin(change_pin_request: commands.ChangePINRequest, authorization: str = fastapi.Header(None)) -> fastapi.Response:
    try:
        print(context.UserContext.get())
        users.change_pin(
            uow=mongo_uow.MongoUOW(),
            cmd=change_pin_request
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except Exception as e:
        return formatters.format_http_response(
            status_code=http.HTTPStatus.BAD_GATEWAY,
            success=True,
            body={},
            errors=[]
        )
