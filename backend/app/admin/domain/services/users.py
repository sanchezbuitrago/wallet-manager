from app.commons import logs
from app.commons.adapters import unit_of_work
from app.auth.domain.model import aggregates

_LOGGER = logs.get_logger()


def list_users(
        cursor: str | None = None,
        limit: int = 20,
        uow: unit_of_work.AbstractUnitOfWork = None,
) -> dict:
    """List all users with cursor-based pagination.

    Args:
        cursor: The ID of the last item from the previous page.
        limit: Maximum number of items per page (max 100).
        uow: Unit of work for data access.

    Returns:
        Dict with items list and next_cursor.
    """
    _LOGGER.info("List users (cursor=%s, limit=%d)", cursor, limit)
    repo = uow.get_repo(entity_type=aggregates.User)

    filters = {}
    if cursor:
        filters["_id"] = {"$lt": cursor}

    users = list(repo.find_by(find=filters, sort_by="_id", descending=True))
    items = users[:limit]

    next_cursor = items[-1].id.value if len(items) == limit else None

    result = [
        {
            "id": u.id.value,
            "first_names": u.first_names,
            "last_names": u.last_names,
            "email": u.email,
            "phone_number": u.phone_number.model_dump(),
            "status": u.status.value,
            "is_admin": u.is_admin,
            "last_login": u.last_login,
        }
        for u in items
    ]

    _LOGGER.info("Listed %d users", len(result))
    return {"items": result, "next_cursor": next_cursor}


def block_user(
        user_id: str,
        uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    """Block a user by setting status to BLOCKED.

    Args:
        user_id: The ID of the user to block.
        uow: Unit of work for data access.
    """
    _LOGGER.info("Block user [%s]", user_id)
    repo = uow.get_repo(entity_type=aggregates.User)
    user = next(repo.find_by(find={"_id": user_id}), None)
    if not user:
        raise Exception("User not found")
    user.block()
    repo.save(new_item=user)
    _LOGGER.info("User [%s] blocked", user_id)


def unblock_user(
        user_id: str,
        uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    """Unblock a user by setting status to ACTIVE.

    Args:
        user_id: The ID of the user to unblock.
        uow: Unit of work for data access.
    """
    _LOGGER.info("Unblock user [%s]", user_id)
    repo = uow.get_repo(entity_type=aggregates.User)
    user = next(repo.find_by(find={"_id": user_id}), None)
    if not user:
        raise Exception("User not found")
    user.unblock()
    repo.save(new_item=user)
    _LOGGER.info("User [%s] unblocked", user_id)


def assign_admin(
        user_id: str,
        uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    """Assign admin privileges to a user.

    Args:
        user_id: The ID of the user to make admin.
        uow: Unit of work for data access.
    """
    _LOGGER.info("Assign admin to user [%s]", user_id)
    repo = uow.get_repo(entity_type=aggregates.User)
    user = next(repo.find_by(find={"_id": user_id}), None)
    if not user:
        raise Exception("User not found")
    user.is_admin = True
    repo.save(new_item=user)
    _LOGGER.info("User [%s] is now admin", user_id)


def revoke_admin(
        user_id: str,
        uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    """Revoke admin privileges from a user.

    Args:
        user_id: The ID of the user to revoke admin from.
        uow: Unit of work for data access.
    """
    _LOGGER.info("Revoke admin from user [%s]", user_id)
    repo = uow.get_repo(entity_type=aggregates.User)
    user = next(repo.find_by(find={"_id": user_id}), None)
    if not user:
        raise Exception("User not found")
    user.is_admin = False
    repo.save(new_item=user)
    _LOGGER.info("User [%s] is no longer admin", user_id)
