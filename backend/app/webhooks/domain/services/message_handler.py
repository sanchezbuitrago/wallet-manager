import pydantic_settings

from app.commons import domain_events
from app.commons.adapters import media_store
from app.webhooks.commons.adapters import ai
from app.commons.adapters import evolution_api
from app.webhooks.domain.model import aggregates
from app.webhooks.domain.model import commands
from app.webhooks.domain.model import entities


class _Settings(pydantic_settings.BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"


_SETTINGS = _Settings()


async def process(cmd: commands.WhatsappEventCommand, uow) -> None:
    """Process an incoming WhatsApp message.

    Validates the sender, downloads audio if present, runs it through
    the AI pipeline, and emits an ApplyMovementRequested event on success.

    Args:
        cmd: The parsed WhatsApp webhook event.
        uow: Unit of work for data access.
    """
    user_repo = uow.get_repo(entities.User)
    message_repo = uow.get_repo(aggregates.Message)

    if not cmd.data.message.audio_message:
        message = aggregates.Message.create(
            user_id="",
            phone_number="",
            remote_jid=cmd.data.key.remote_jid,
            content="not_audio",
            message_type="TEXT"
        )
        async with uow.transaction():
            message_repo.save(new_item=message)
            uow.add_event(domain_events.WhatsAppMessageRequested(
                remote_jid=cmd.data.key.remote_jid,
                message="Actualmente solo permitimos mensajes de audio"
            ))
        return

    if cmd.data.key.from_me:
        return

    jid = cmd.data.key.remote_jid
    number = jid.split("@")[0] if "@s.whatsapp.net" in jid else jid

    user = next(user_repo.find_by(find={"full_phone": number}), None)
    if not user:
        message = aggregates.Message.create(
            user_id="",
            phone_number=number,
            remote_jid=jid,
            content="unregistered_user",
            message_type="TEXT"
        )
        async with uow.transaction():
            message_repo.save(new_item=message)
            uow.add_event(domain_events.WhatsAppMessageRequested(
                remote_jid=jid,
                message="No se encontró un usuario registrado con este número"
            ))
        return

    uow.add_event(domain_events.WhatsAppMessageRequested(
        remote_jid=jid,
        message="Procesando solicitud"
    ))

    evo = evolution_api.DefaultEvolutionApiAdapter()
    media_file = await evo.get_media_file(message_id=cmd.data.key.id)
    media_adapter = media_store.LocalMediaAdapter()
    media_url = media_adapter.save(media_file.base_64, media_file.mimetype)

    message = aggregates.Message.create(
        user_id=user.id.value,
        phone_number=number,
        remote_jid=jid,
        content="audio",
        message_type="AUDIO",
        media_url=media_url
    )

    ai_adapter = ai.GeminiAIAdapter(
        api_key=_SETTINGS.gemini_api_key,
        model=_SETTINGS.gemini_model
    )
    result = await ai_adapter.analyze_audio(
        audio_base64=media_file.base_64,
        mime_type=media_file.mimetype
    )

    if not result.success or result.amount is None:
        async with uow.transaction():
            message_repo.save(new_item=message)
            uow.add_event(domain_events.WhatsAppMessageRequested(
                remote_jid=jid,
                message="No se pudo procesar el audio. Intenta de nuevo."
            ))
        return

    async with uow.transaction():
        message_repo.save(new_item=message)
        uow.add_event(domain_events.ApplyMovementRequested(
            idempotency_key=message.id.value,
            user_id=user.id.value,
            amount=result.amount,
            category=result.category or "",
            description=result.description or "",
            movement_type=result.movement_type or ""
        ))
