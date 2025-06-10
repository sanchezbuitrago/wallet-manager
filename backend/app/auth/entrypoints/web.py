import json
import fastapi

from app.commons.adapters import unit_of_work
from app.auth.domain.model import commands, exceptions
from app.commons import standard_types

from app.auth.domain.services import users

auth_routes = fastapi.APIRouter()

@auth_routes.post("/")
async def create_user(create_user_request: commands.CreateUserRequest) -> fastapi.Response:
    try:
        users.create_user(uow=unit_of_work.FakeUnitOfWork(), cmd=create_user_request)
        return fastapi.Response(content=json.dumps(standard_types.ApiResponse(
            success=True,
            body={},
            errors=[]
        ).model_dump()))
    except exceptions.UserAlreadyExistError:
        return fastapi.Response(content=json.dumps(standard_types.ApiResponse(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="User Already Exist",
                    code="USER_ALREADY_EXIST",
                    detail=f"User with email [{create_user_request.email}] already exist"
                )
            ]
        ).model_dump()))