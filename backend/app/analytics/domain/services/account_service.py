from app.commons import logs
from app.commons.adapters import unit_of_work
from app.analytics.domain.model import dtos, entities

_LOGGER = logs.get_logger()


def list_accounts_by_user(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
) -> list[dtos.AccountResponse]:
    _LOGGER.info("Listing accounts for user [%s]", user_id)
    repo = uow.get_repo(entity_type=entities.Account)
    accounts = list(repo.find_by(find={"user_id": user_id}, sort_by="created_at", descending=False))
    _LOGGER.info("Found [%d] accounts for user [%s]", len(accounts), user_id)
    return [
        dtos.AccountResponse(
            id=a.id.value,
            user_id=a.user_id,
            balance=str(a.balance.amount),
            currency=a.balance.currency,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in accounts
    ]
