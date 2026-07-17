from app.commons import domain_events
from app.commons import event_bus as eb
from app.commons.adapters import mongo_uow
from app.webhooks.domain.model import aggregates


@eb.event_handler(domain_events.MovementApplied)
async def on_movement_applied(event: domain_events.MovementApplied) -> None:
    """Confirm to the user that a movement was applied successfully."""
    uow = mongo_uow.MongoUOW()
    message_repo = uow.get_repo(aggregates.Message)
    message = next(
        message_repo.find_by(find={"_id": event.idempotency_key}),
        None
    )

    if message and not message.responded:
        async with uow.transaction():
            message.responded = True
            message_repo.save(new_item=message)
            uow.add_event(domain_events.WhatsAppMessageRequested(
                remote_jid=message.remote_jid,
                message=(
                    f"Se van a cargar los siguientes datos:\n"
                    f"Amount: {event.amount}\n"
                    f"Category: {event.category}\n"
                    f"Description: {event.description}\n"
                    f"Tipo de movimiento: {event.movement_type}"
                )
            ))


@eb.event_handler(domain_events.MovementApplicationFailed)
async def on_movement_application_failed(
    event: domain_events.MovementApplicationFailed,
) -> None:
    """Notify the user that the movement could not be processed."""
    uow = mongo_uow.MongoUOW()
    message_repo = uow.get_repo(aggregates.Message)
    message = next(
        message_repo.find_by(find={"_id": event.idempotency_key}),
        None
    )

    if message and not message.responded:
        async with uow.transaction():
            message.responded = True
            message_repo.save(new_item=message)
            uow.add_event(domain_events.WhatsAppMessageRequested(
                remote_jid=message.remote_jid,
                message=event.error_message
            ))
