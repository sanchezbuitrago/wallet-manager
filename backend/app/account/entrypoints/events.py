from app.commons import domain_events
from app.commons import event_bus as eb


@eb.event_handler(domain_events.ApplyMovementRequested)
async def on_apply_movement_requested(
    event: domain_events.ApplyMovementRequested,
) -> None:
    """Convert an ApplyMovementRequested event into a movement command."""
    from app.commons.adapters import mongo_uow
    from app.account.domain.model import commands
    from app.account.domain.services import movement_service

    uow = mongo_uow.MongoUOW()
    cmd = commands.ProcessMovementCommand(
        idempotency_key=event.idempotency_key,
        user_id=event.user_id,
        amount=event.amount,
        category=event.category,
        description=event.description,
        movement_type=event.movement_type
    )
    await movement_service.process(cmd, uow)


@eb.event_handler(domain_events.UserCreated)
async def on_user_created(
    event: domain_events.UserCreated,
) -> None:
    """Create a zero-balance account for a newly verified user."""
    from app.commons import logs
    from app.commons.adapters import mongo_uow
    from app.account.domain.model import aggregates

    _LOGGER = logs.get_logger()
    _LOGGER.info("Creating account for new user [%s]", event.user_id)

    uow = mongo_uow.MongoUOW()
    account_repo = uow.get_repo(aggregates.Account)
    account = aggregates.Account.create(user_id=event.user_id)
    account_repo.save(new_item=account)
    _LOGGER.info("Account [%s] created for user [%s]", account.id.value, event.user_id)
