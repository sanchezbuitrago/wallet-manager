from app.commons import domain_events
from app.commons import event_bus as eb
from app.commons.adapters import mongo_uow
from app.notification.domain.model import commands
from app.notification.domain.services import notification_service


@eb.event_handler(domain_events.WhatsAppMessageRequested)
async def on_whatsapp_message_requested(
    event: domain_events.WhatsAppMessageRequested,
) -> None:
    """Convert a WhatsAppMessageRequested event into a send command."""
    uow = mongo_uow.MongoUOW()
    cmd = commands.SendWhatsAppMessageCommand(
        remote_jid=event.remote_jid,
        message=event.message
    )
    await notification_service.deliver(cmd, uow)


@eb.event_handler(domain_events.TokenRequested)
async def on_token_requested(
    event: domain_events.TokenRequested,
) -> None:
    """Send verification code via WhatsApp when a token is requested."""
    message = (
        f"Tu codigo de verificacion de Wallet Manager es: {event.verification_code}\n"
        f"Este codigo expira en 5 minutos."
    )
    uow = mongo_uow.MongoUOW()
    cmd = commands.SendWhatsAppMessageCommand(
        remote_jid=event.phone_number,
        message=message
    )
    await notification_service.deliver(cmd, uow)


@eb.event_handler(domain_events.TokenVerified)
async def on_token_verified(
    event: domain_events.TokenVerified,
) -> None:
    """Send welcome message via WhatsApp when a user is verified."""
    message = (
        "Bienvenido a Wallet Manager! 🎉\n"
        "Tu cuenta ha sido verificada correctamente.\n"
        "Ya puedes iniciar sesion con tu correo y PIN."
    )
    uow = mongo_uow.MongoUOW()
    cmd = commands.SendWhatsAppMessageCommand(
        remote_jid=event.phone_number,
        message=message
    )
    await notification_service.deliver(cmd, uow)
