from typing import Callable, Coroutine

from app.commons import logs
from app.commons.base_types import Money
from app.commons.adapters import media_store
from app.commons.adapters import unit_of_work
from app.webhooks.commons.adapters import evolution_api
from app.webhooks.commons.adapters import ai
from app.webhooks.domain.model import commands
from app.webhooks.domain.model import aggregates
from app.webhooks.domain.model import entities

_LOGGER = logs.get_logger()


async def process_message_upsert_event(
        cmd: commands.WhatsappEventCommand,
        evolution_api_adapter: evolution_api.EvolutionApiAdapter,
        uow: unit_of_work.AbstractUnitOfWork,
        media_adapter: media_store.AbstractMediaAdapter,
        ai_adapter: ai.AIAdapter
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

    user_id = user.id.value
    _LOGGER.info("User [%s] sent message from [%s]", user_id, number)

    await evolution_api_adapter.send_text_message(jid=jid, message="Procesando solicitud🏃")
    media_file = await evolution_api_adapter.get_media_file(message_id=cmd.data.key.id)
    media_url = media_adapter.save(media_file.base_64, media_file.mimetype)
    _LOGGER.info("Media saved at %s for message [%s]", media_url, cmd.data.key.id)

    message = aggregates.Message.create(
        user_id=user_id,
        phone_number=number,
        remote_jid=jid,
        content="audio",
        message_type="AUDIO",
        media_url=media_url
    )
    message_repo.save(new_item=message)
    _LOGGER.info("Message [%s] saved for user [%s] with media [%s]", message.id.value, user_id, media_url)

    result = await ai_adapter.analyze_audio(
        audio_base64=media_file.base_64,
        mime_type=media_file.mimetype
    )

    if result.success:
        message.processing_result = aggregates.ProcessingResult(
            success=True,
            money=Money(amount=result.amount) if result.amount is not None else None,
            category=result.category,
            description=result.description,
            movement_type=result.movement_type
        )
        message_repo.save(new_item=message)

        if result.amount is None:
            _LOGGER.error("AI returned success but amount is null for message [%s]", message.id.value)
            await evolution_api_adapter.send_text_message(jid=jid, message="No se pudo determinar el monto del audio. Por favor intenta de nuevo.")
            return

        account_repo = uow.get_repo(entity_type=aggregates.Account)
        account = next(account_repo.find_by(find={"user_id": user_id}), None)
        if not account:
            account = aggregates.Account.create(user_id=user_id)
            account_repo.save(new_item=account)
            _LOGGER.info("Account [%s] created for user [%s]", account.id.value, user_id)

        amount = result.amount
        opening_balance = Money(amount=account.balance.amount)
        if result.movement_type == "INCOME":
            account.credit(amount=amount)
        else:
            account.debit(amount=amount)
        closing_balance = Money(amount=account.balance.amount)
        account_repo.save(new_item=account)

        movement = aggregates.Movement.create(
            account_id=account.id.value,
            user_id=user_id,
            money=Money(amount=amount),
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            category=result.category or "",
            description=result.description or "",
            movement_type=result.movement_type or ""
        )
        movement_repo = uow.get_repo(entity_type=aggregates.Movement)
        movement_repo.save(new_item=movement)
        _LOGGER.info("Movement [%s] saved for account [%s]", movement.id.value, account.id.value)

        money = Money(amount=amount)
        message_text = (
            "Se van a cargar los siguientes datos:\n"
            f"Amount: {money.amount} {money.currency}\n"
            f"Category: {result.category}\n"
            f"Description: {result.description}\n"
            f"MovementType: {result.movement_type}"
        )
        _LOGGER.info("Sending confirmation message: %s", message_text)
        await evolution_api_adapter.send_text_message(jid=jid, message=message_text)
    else:
        _LOGGER.error("AI analysis failed for message [%s]: %s", message.id.value, result.error_message)
        message.processing_result = aggregates.ProcessingResult(
            success=False,
            error_message=result.error_message
        )
        message_repo.save(new_item=message)
        await evolution_api_adapter.send_text_message(jid=jid, message=result.error_message)


_EVENTS_PROCESSOR: dict[str, Callable] = {
    "messages.upsert": process_message_upsert_event
}


async def process_event(
        cmd: commands.WhatsappEventCommand,
        evolution_api_adapter: evolution_api.EvolutionApiAdapter,
        uow: unit_of_work.AbstractUnitOfWork,
        media_adapter: media_store.AbstractMediaAdapter,
        ai_adapter: ai.AIAdapter
) -> None:
    processor = _EVENTS_PROCESSOR.get(cmd.event)
    if processor:
        await processor(
            cmd=cmd,
            evolution_api_adapter=evolution_api_adapter,
            uow=uow,
            media_adapter=media_adapter,
            ai_adapter=ai_adapter
        )
    else:
        _LOGGER.warning("Event processor not found for event: %s", cmd.event)
