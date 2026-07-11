from typing import Callable, Coroutine
from app.commons import logs
from app.commons.adapters import media_store, unit_of_work
from app.webhooks.commons.adapters import evolution_api
from app.webhooks.domain.model import commands
from app.webhooks.commons.adapters.n8n import n8n_adapter
from app.webhooks.commons.adapters.n8n.domain import model as n8n_model
from app.webhooks.domain.model import entities, aggregates

_LOGGER = logs.get_logger()


async def process_message_upsert_event(
        cmd: commands.WhatsappEventCommand,
        evolution_api_adapter: evolution_api.EvolutionApiAdapter,
        uow: unit_of_work.AbstractUnitOfWork,
        media_adapter: media_store.AbstractMediaAdapter
) -> None:
    _LOGGER.info("Processing new upsert event")
    _LOGGER.debug("Event payload: %s", cmd.model_dump_json())

    user_repo = uow.get_repo(entity_type=entities.User)
    message_repo = uow.get_repo(entity_type=aggregates.Message)

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

    user = next(user_repo.find_by(find={"full_phone": number}), None)
    if not user:
        _LOGGER.info("Unregistered user sent message from [%s]", number)
        await evolution_api_adapter.send_text_message(jid=jid, message="No se encontró un usuario registrado con este número. Por favor registra tu cuenta primero.")
        return

    _LOGGER.info("User [%s] sent message from [%s]", user.id.value, number)

    await evolution_api_adapter.send_text_message(jid=jid, message="Procesando solicitud🏃")
    media_file = await evolution_api_adapter.get_media_file(message_id=cmd.data.key.id)
    media_url = media_adapter.save(media_file.base_64, media_file.mimetype)
    _LOGGER.info("Media saved at %s for message [%s]", media_url, cmd.data.key.id)

    message = aggregates.Message.create(
        user_id=user.id.value,
        phone_number=number,
        remote_jid=jid,
        content="audio",
        message_type="AUDIO",
        media_url=media_url
    )
    message_repo.save(new_item=message)
    _LOGGER.info("Message [%s] saved for user [%s] with media [%s]", message.id.value, user.id.value, media_url)

    n8n = n8n_adapter.DefaultN8NAdapter()
    await n8n.send_message_to_webhook(
        message=n8n_model.N8NMediaFile(
            type=n8n_model.MessageType.AUDIO,
            user_id=user.id.value,
            message_id=message.id.value,
            media_file=n8n_model.MediaFile(
                file_name=media_file.file_name,
                media_type=media_file.media_type,
                base_64=media_file.base_64,
                mime_type=media_file.mimetype
            )
        )
    )


_EVENTS_PROCESSOR: dict[str, Callable[[commands.WhatsappEventCommand, evolution_api.EvolutionApiAdapter, unit_of_work.AbstractUnitOfWork, media_store.AbstractMediaAdapter], Coroutine[None, None, None]]] = {
    "messages.upsert": process_message_upsert_event
}

async def process_event(
        cmd: commands.WhatsappEventCommand,
        evolution_api_adapter: evolution_api.EvolutionApiAdapter,
        uow: unit_of_work.AbstractUnitOfWork,
        media_adapter: media_store.AbstractMediaAdapter
) -> None:
    processor = _EVENTS_PROCESSOR.get(cmd.event)
    if processor:
        await processor(cmd=cmd, evolution_api_adapter=evolution_api_adapter, uow=uow, media_adapter=media_adapter)
    else:
        _LOGGER.warning("Event processor not found for event: %s", cmd.event)


