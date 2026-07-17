from app.commons import logs
from app.commons import standard_types
from app.commons.adapters import unit_of_work
from app.analytics.domain.model import dtos
from app.analytics.domain.model import entities

_LOGGER = logs.get_logger()


def list_movements(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
    account_id: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
    category: str | None = None,
    movement_type: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dtos.MovementPageResponse:
    """List movements for a user with optional filters and cursor pagination.

    Args:
        uow: Unit of work for data access.
        user_id: The user whose movements to list.
        account_id: Optional account filter.
        cursor: Optional cursor for pagination.
        limit: Maximum number of results (capped at 100).
        category: Optional category filter.
        movement_type: Optional type filter (INCOME/EXPENSE).
        from_date: Optional start date (ISO-8601).
        to_date: Optional end date (ISO-8601).

    Returns:
        A paginated movement response.
    """
    _LOGGER.info("Listing movements for user [%s]", user_id)

    repo = uow.get_repo(entity_type=entities.Movement)

    filters: dict = {"user_id": user_id}
    if account_id:
        filters["account_id"] = account_id
    if cursor:
        filters["_id"] = {"$lt": cursor}
    if category:
        filters["category"] = category
    if movement_type:
        filters["movement_type"] = movement_type
    if from_date:
        filters["created_at.value"] = filters.get("created_at.value", {})
        from_ts = standard_types.Timestamp.from_string(from_date)
        filters["created_at.value"]["$gte"] = from_ts.value
    if to_date:
        filters["created_at.value"] = filters.get("created_at.value", {})
        to_ts = standard_types.Timestamp.from_string(to_date)
        filters["created_at.value"]["$lte"] = to_ts.value

    movements = list(repo.find_by(
        find=filters,
        sort_by="_id",
        descending=True,
    ))[:limit]

    items = [
        dtos.MovementResponse(
            id=m.id.value,
            account_id=m.account_id,
            user_id=m.user_id,
            amount=str(m.money.amount),
            currency=m.money.currency,
            opening_balance=str(m.opening_balance.amount),
            closing_balance=str(m.closing_balance.amount),
            category=m.category,
            description=m.description,
            movement_type=m.movement_type,
            created_at=m.created_at,
        )
        for m in movements
    ]

    next_cursor = items[-1].id if len(items) == limit else None

    return dtos.MovementPageResponse(items=items, next_cursor=next_cursor)


def get_movement(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
    movement_id: str,
) -> dtos.MovementResponse | None:
    """Get a single movement by ID, ensuring it belongs to the user.

    Args:
        uow: Unit of work for data access.
        user_id: The owning user's ID.
        movement_id: The movement ID to look up.

    Returns:
        The movement response, or None if not found or not owned.
    """
    _LOGGER.info("Getting movement [%s] for user [%s]", movement_id, user_id)
    repo = uow.get_repo(entity_type=entities.Movement)
    movement = repo.find_by_id(entity_id=entities.MovementId(id=movement_id))
    if not movement or movement.user_id != user_id:
        _LOGGER.info(
            "Movement [%s] not found or not owned by user [%s]",
            movement_id,
            user_id,
        )
        return None
    return dtos.MovementResponse(
        id=movement.id.value,
        account_id=movement.account_id,
        user_id=movement.user_id,
        amount=str(movement.money.amount),
        currency=movement.money.currency,
        opening_balance=str(movement.opening_balance.amount),
        closing_balance=str(movement.closing_balance.amount),
        category=movement.category,
        description=movement.description,
        movement_type=movement.movement_type,
        created_at=movement.created_at,
    )
