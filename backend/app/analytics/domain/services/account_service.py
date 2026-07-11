from app.commons import logs
from app.commons.adapters import unit_of_work
from app.analytics.domain.model import dtos, entities

_LOGGER = logs.get_logger()


def get_account_by_user(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
) -> dtos.AccountResponse | None:
    _LOGGER.info("Looking for account for user [%s]", user_id)
    repo = uow.get_repo(entity_type=entities.Account)
    account = next(repo.find_by(find={"user_id": user_id}), None)
    if not account:
        _LOGGER.info("No account found for user [%s]", user_id)
        return None
    _LOGGER.info("Account [%s] found for user [%s]", account.id.value, user_id)
    return dtos.AccountResponse(
        id=account.id.value,
        user_id=account.user_id,
        balance=str(account.balance.amount),
        currency=account.balance.currency,
    )
