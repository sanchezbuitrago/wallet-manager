import fastapi

from app.commons import context
from app.commons import logs
from app.commons.adapters import mongo_uow
from app.commons import formatters
from app.commons import standard_types
from app.commons import wrappers
from app.analytics.domain.services import account_service
from app.analytics.domain.services import movement_service
from app.analytics.domain.services import stats_service

_LOGGER = logs.get_logger()

analytics_routes = fastapi.APIRouter()


@analytics_routes.get("/accounts")
@wrappers.authentication_required
async def list_accounts(
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """List all accounts for the authenticated user."""
    user_id = context.UserContext.get()
    _LOGGER.info("Listing accounts for user [%s]", user_id)
    accounts = account_service.list_accounts_by_user(
        uow=mongo_uow.MongoUOW(),
        user_id=user_id,
    )
    return formatters.format_http_response(
        success=True,
        body={"items": [a.model_dump() for a in accounts]},
        errors=[],
    )


@analytics_routes.get("/movements")
@wrappers.authentication_required
async def list_movements(
    account_id: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
    category: str | None = None,
    movement_type: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """List movements with optional filters and cursor pagination."""
    user_id = context.UserContext.get()
    page = movement_service.list_movements(
        uow=mongo_uow.MongoUOW(),
        user_id=user_id,
        account_id=account_id,
        cursor=cursor,
        limit=min(limit, 100),
        category=category,
        movement_type=movement_type,
        from_date=from_date,
        to_date=to_date,
    )
    return formatters.format_http_response(
        success=True,
        body=page.model_dump(),
        errors=[],
    )


@analytics_routes.get("/movements/{movement_id}")
@wrappers.authentication_required
async def get_movement(
    movement_id: str,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Get a single movement by ID."""
    user_id = context.UserContext.get()
    movement = movement_service.get_movement(
        uow=mongo_uow.MongoUOW(),
        user_id=user_id,
        movement_id=movement_id,
    )
    if not movement:
        return formatters.format_http_response(
            success=False,
            body={},
            errors=[
                standard_types.ApiError(
                    title="Movement not found",
                    code="ANALYTICS/MOVEMENT_NOT_FOUND",
                    detail="Movement not found or not owned by the current user",
                )
            ],
        )
    return formatters.format_http_response(
        success=True,
        body=movement.model_dump(),
        errors=[],
    )


@analytics_routes.get("/stats/by-category")
@wrappers.authentication_required
async def stats_by_category(
    account_id: str | None = None,
    category: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Get movement totals grouped by category."""
    user_id = context.UserContext.get()
    stats = stats_service.by_category(
        uow=mongo_uow.MongoUOW(),
        user_id=user_id,
        account_id=account_id,
        category=category,
        from_date=from_date,
        to_date=to_date,
    )
    return formatters.format_http_response(
        success=True,
        body={"items": [s.model_dump() for s in stats]},
        errors=[],
    )


@analytics_routes.get("/stats/monthly")
@wrappers.authentication_required
async def stats_monthly(
    account_id: str | None = None,
    months: int = 6,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Get monthly income and expense totals."""
    user_id = context.UserContext.get()
    stats = stats_service.monthly(
        uow=mongo_uow.MongoUOW(),
        user_id=user_id,
        account_id=account_id,
        months=months,
    )
    return formatters.format_http_response(
        success=True,
        body={"items": [s.model_dump() for s in stats]},
        errors=[],
    )


@analytics_routes.get("/stats/weekly")
@wrappers.authentication_required
async def stats_weekly(
    account_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Get weekly stats with daily breakdown."""
    user_id = context.UserContext.get()
    stats = stats_service.weekly(
        uow=mongo_uow.MongoUOW(),
        user_id=user_id,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
    )
    return formatters.format_http_response(
        success=True,
        body=stats.model_dump(),
        errors=[],
    )


@analytics_routes.get("/stats/summary")
@wrappers.authentication_required
async def stats_summary(
    account_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    authorization: str = fastapi.Header(None),
) -> fastapi.Response:
    """Get an aggregate summary of balance and movement totals."""
    user_id = context.UserContext.get()
    stats = stats_service.summary(
        uow=mongo_uow.MongoUOW(),
        user_id=user_id,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
    )
    return formatters.format_http_response(
        success=True,
        body=stats.model_dump(),
        errors=[],
    )
