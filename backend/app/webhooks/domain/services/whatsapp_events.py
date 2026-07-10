from typing import Callable, Coroutine
from app.commons import logs
from app.commons.adapters import unit_of_work
from app.webhooks.commons.adapters import evolution_api
from app.webhooks.domain.model import commands
from app.webhooks.commons.adapters.n8n import n8n_adapter
from app.webhooks.commons.adapters.n8n.domain import model as n8n_model

_LOGGER = logs.get_logger()


async def process_message_upsert_event(
        cmd: commands.WhatsappEventCommand,
        evolution_api_adapter: evolution_api.EvolutionApiAdapter,
        uow: unit_of_work.AbstractUnitOfWork
) -> None:
    _LOGGER.info("Processing new upsert event")
    _LOGGER.debug("Event payload: %s", cmd.model_dump_json())
    if not cmd.data.message.audio_message:
        _LOGGER.info("Message avoided because it is not a audio message")
        await evolution_api_adapter.send_text_message(jid=cmd.data.key.remote_jid, message="Actualmente solo permitimos mensajes de audio 😭")
        return
    if cmd.data.key.from_me:
        _LOGGER.info("Message avoided because is a message sent from me")
        return

    jid = cmd.data.key.remote_jid
    if "@s.whatsapp.net" in jid:
        number = jid.split("@")[0]
    else:
        number = jid

    await evolution_api_adapter.send_text_message(jid=jid, message="Procesando solicitud🏃")
    media_file = await evolution_api_adapter.get_media_file(message_id=cmd.data.key.id)
    # TODO: Recibir adaptador por parametro
    n8n = n8n_adapter.DefaultN8NAdapter()
    await n8n.send_message_to_webhook(
        message=n8n_model.N8NMediaFile(
            type=n8n_model.MessageType.AUDIO,
            number=jid,
            media_file=n8n_model.MediaFile(
                file_name=media_file.file_name,
                media_type=media_file.media_type,
                base_64=media_file.base_64,
                mime_type=media_file.mimetype
            )
        )
    )


    #await evolution_api_adapter.get_profile(number=number)


_EVENTS_PROCESSOR: dict[str, Callable[[commands.WhatsappEventCommand, evolution_api.EvolutionApiAdapter, unit_of_work.AbstractUnitOfWork], Coroutine[None, None, None]]] = {
    "messages.upsert": process_message_upsert_event
}

async def process_event(
        cmd: commands.WhatsappEventCommand,
        evolution_api_adapter: evolution_api.EvolutionApiAdapter,
        uow: unit_of_work.AbstractUnitOfWork
) -> None:
    processor = _EVENTS_PROCESSOR.get(cmd.event)
    if processor:
        await processor(cmd=cmd, evolution_api_adapter=evolution_api_adapter, uow=uow)
    else:
        _LOGGER.warning("Event processor not found for event: %s", cmd.event)


