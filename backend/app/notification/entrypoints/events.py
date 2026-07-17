from app.commons import domain_events
from app.commons import event_bus as eb
from app.commons.adapters import mongo_uow
from app.notification.domain.model import commands
from app.notification.domain.services import notification_service


@eb.event_handler(domain_events.WhatsAppMessageRequested)
async def on_whatsapp_message_requested(
    event: domain_events.WhatsAppMessageRequested
) -> None:
    uow = mongo_uow.MongoUOW()
    cmd = commands.SendWhatsAppMessageCommand(
        remote_jid=event.remote_jid,
        message=event.message
    )
    await notification_service.deliver(cmd, uow)
