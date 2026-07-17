from app.commons.adapters import evolution_api
from app.notification.domain.model import commands


async def deliver(cmd: commands.SendWhatsAppMessageCommand, uow) -> None:
    """Send a WhatsApp message via the Evolution API.

    Args:
        cmd: The message command containing JID and text.
        uow: Unit of work (unused but kept for interface consistency).
    """
    evo = evolution_api.DefaultEvolutionApiAdapter()
    await evo.send_text_message(jid=cmd.remote_jid, message=cmd.message)
