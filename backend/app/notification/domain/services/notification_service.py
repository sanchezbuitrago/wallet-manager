from app.commons.adapters import evolution_api
from app.notification.domain.model import commands


async def deliver(cmd: commands.SendWhatsAppMessageCommand, uow) -> None:
    evo = evolution_api.DefaultEvolutionApiAdapter()
    await evo.send_text_message(jid=cmd.remote_jid, message=cmd.message)
