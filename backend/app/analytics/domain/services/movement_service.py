from app.commons import logs, standard_types
from app.commons.adapters import unit_of_work
from app.analytics.domain.model import dtos, entities

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
        filters["created_at.value"]["$gte"] = standard_types.Timestamp.from_string(from_date).value
    if to_date:
        filters["created_at.value"] = filters.get("created_at.value", {})
        filters["created_at.value"]["$lte"] = standard_types.Timestamp.from_string(to_date).value

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
    _LOGGER.info("Getting movement [%s] for user [%s]", movement_id, user_id)
    repo = uow.get_repo(entity_type=entities.Movement)
    movement = repo.find_by_id(entity_id=entities.MovementId(id=movement_id))
    if not movement or movement.user_id != user_id:
        _LOGGER.info("Movement [%s] not found or not owned by user [%s]", movement_id, user_id)
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