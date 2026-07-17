from app.commons import logs
from app.commons import domain_events
from app.commons.adapters import unit_of_work
from app.commons import base_types
from app.account.domain.model import aggregates
from app.account.domain.model import commands

_LOGGER = logs.get_logger()


async def process(cmd: commands.ProcessMovementCommand, uow: unit_of_work.AbstractUnitOfWork) -> None:
    """Apply a movement to the user's account.

    Debits or credits the account, persists the movement, and emits
    a MovementApplied or MovementApplicationFailed event.

    Args:
        cmd: The movement command to process.
        uow: Unit of work for data access.
    """
    try:
        account_repo = uow.get_repo(aggregates.Account)
        movement_repo = uow.get_repo(aggregates.Movement)

        account = next(
            account_repo.find_by(find={"user_id": cmd.user_id}),
            None
        )
        if not account:
            account = aggregates.Account.create(user_id=cmd.user_id)

        opening_balance = base_types.Money(amount=account.balance.amount)
        if cmd.movement_type == "INCOME":
            account.credit(amount=cmd.amount)
        else:
            account.debit(amount=cmd.amount)
        closing_balance = base_types.Money(amount=account.balance.amount)

        movement = aggregates.Movement.create(
            account_id=account.id.value,
            user_id=cmd.user_id,
            money=base_types.Money(amount=cmd.amount),
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            category=cmd.category,
            description=cmd.description,
            movement_type=cmd.movement_type
        )

        async with uow.transaction():
            account_repo.save(new_item=account)
            movement_repo.save(new_item=movement)
            uow.add_event(domain_events.MovementApplied(
                idempotency_key=cmd.idempotency_key,
                user_id=cmd.user_id,
                amount=cmd.amount,
                category=cmd.category,
                description=cmd.description,
                movement_type=cmd.movement_type
            ))
    except Exception as e:
        _LOGGER.error("Failed to apply movement: %s", e)
        uow.add_event(domain_events.MovementApplicationFailed(
            idempotency_key=cmd.idempotency_key,
            user_id=cmd.user_id,
            error_message="No se pudo procesar el movimiento. Intenta de nuevo."
        ))
