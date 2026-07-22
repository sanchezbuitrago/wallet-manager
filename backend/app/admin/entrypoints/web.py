import http

import fastapi

from app.commons import context
from app.commons import logs
from app.commons import wrappers
from app.commons import formatters
from app.commons import standard_types
from app.commons.adapters import mongo_uow
from app.admin.domain.services import users as admin_users

_LOGGER = logs.get_logger()

admin_routes = fastapi.APIRouter()


@admin_routes.get("/users")
@wrappers.authentication_required(admin_required=True)
async def list_users(
    cursor: str | None = None,
    limit: int = 20,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """List all users with cursor-based pagination."""
    try:
        result = admin_users.list_users(
            cursor=cursor,
            limit=min(limit, 100),
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body=result,
            errors=[]
        )
    except Exception as e:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Error",
                    code="INTERNAL_ERROR",
                    detail=str(e)
                )
            ]
        )


@admin_routes.patch("/users/{user_id}/block")
@wrappers.authentication_required(admin_required=True)
async def block_user(
    user_id: str,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Block a user."""
    try:
        admin_users.block_user(
            user_id=user_id,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except Exception as e:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Error",
                    code="INTERNAL_ERROR",
                    detail=str(e)
                )
            ]
        )


@admin_routes.patch("/users/{user_id}/unblock")
@wrappers.authentication_required(admin_required=True)
async def unblock_user(
    user_id: str,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Unblock a user."""
    try:
        admin_users.unblock_user(
            user_id=user_id,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except Exception as e:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Error",
                    code="INTERNAL_ERROR",
                    detail=str(e)
                )
            ]
        )


@admin_routes.patch("/users/{user_id}/admin")
@wrappers.authentication_required(admin_required=True)
async def assign_admin(
    user_id: str,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Assign admin privileges to a user."""
    try:
        admin_users.assign_admin(
            user_id=user_id,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except Exception as e:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Error",
                    code="INTERNAL_ERROR",
                    detail=str(e)
                )
            ]
        )


@admin_routes.patch("/users/{user_id}/revoke-admin")
@wrappers.authentication_required(admin_required=True)
async def revoke_admin(
    user_id: str,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Revoke admin privileges from a user."""
    try:
        admin_users.revoke_admin(
            user_id=user_id,
            uow=mongo_uow.MongoUOW(),
        )
        return formatters.format_http_response(
            success=True,
            body={},
            errors=[]
        )
    except Exception as e:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Error",
                    code="INTERNAL_ERROR",
                    detail=str(e)
                )
            ]
        )
