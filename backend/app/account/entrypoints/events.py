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
