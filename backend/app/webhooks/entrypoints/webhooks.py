import fastapi
import pydantic_settings

from app.commons import logs
from app.commons.adapters import media_store, mongo_uow
from app.webhooks.commons.adapters import evolution_api
from app.commons.base_types import Money
from app.webhooks.domain.model import commands, aggregates
from app.webhooks.domain.services import whatsapp_events

_LOGGER = logs.get_logger()

webhooks_routes = fastapi.APIRouter()


class _Settings(pydantic_settings.BaseSettings):
    auth_secret_key: str
    algorithm: str


_SETTINGS = _Settings()

@webhooks_routes.post("/whatsapp")
async def whatsapp_webhook(request: fastapi.Request) -> fastapi.Response:
   body = await request.json()

   #TODO Almacenar mensajes y crear endpoint para descarga de archivos y hacer llamado desde n8n ?
   _LOGGER.debug("WhatsApp webhook body: %s", body)


   cmd = commands.WhatsappEventCommand.model_validate(body)
   await whatsapp_events.process_event(
       cmd=cmd,
       evolution_api_adapter=evolution_api.DefaultEvolutionApiAdapter(),
       uow=mongo_uow.MongoUOW(),
       media_adapter=media_store.LocalMediaAdapter()
   )
   return fastapi.Response(status_code=200)


@webhooks_routes.post("/n8n")
async def n8n_webhook(request: fastapi.Request) -> fastapi.Response:
    data = await request.json()
    _LOGGER.info("n8n webhook body: %s", data)
    evo_api = evolution_api.DefaultEvolutionApiAdapter()
    uow = mongo_uow.MongoUOW()

    response = commands.N8NWebhookResponse.model_validate(data)

    message_repo = uow.get_repo(entity_type=aggregates.Message)
    message = message_repo.find_by_id(entity_id=aggregates.MessageId(id=response.message_id))

    if not message:
        _LOGGER.error("Message [%s] not found for user [%s]", response.message_id, response.user_id)
        return fastapi.Response(status_code=200)

    jid = message.remote_jid

    if response.success:
        message.processing_result = aggregates.ProcessingResult(
            success=True,
            money=Money(amount=response.payload.amount),
            category=response.payload.category,
            description=response.payload.description,
            movement_type=response.payload.movement_type,
            error_message=response.error_message
        )
        message_repo.save(new_item=message)

        if response.error_message:
            _LOGGER.error("Error desde n8n: %s", response.error_message)
            await evo_api.send_text_message(jid=jid, message=response.error_message)
        else:
            account_repo = uow.get_repo(entity_type=aggregates.Account)
            account = next(account_repo.find_by(find={"user_id": response.user_id}), None)
            if not account:
                account = aggregates.Account.create(user_id=response.user_id)
                account_repo.save(new_item=account)
                _LOGGER.info("Account [%s] created for user [%s]", account.id.value, response.user_id)

            amount = response.payload.amount
            if response.payload.movement_type == "INCOME":
                account.credit(amount=amount)
            else:
                account.debit(amount=amount)
            account_repo.save(new_item=account)

            movement = aggregates.Movement.create(
                account_id=account.id.value,
                user_id=response.user_id,
                money=Money(amount=amount),
                category=response.payload.category,
                description=response.payload.description,
                movement_type=response.payload.movement_type
            )
            movement_repo = uow.get_repo(entity_type=aggregates.Movement)
            movement_repo.save(new_item=movement)
            _LOGGER.info("Movement [%s] saved for account [%s]", movement.id.value, account.id.value)
            money = Money(amount=amount)
            message_text = (
                "Se van a cargar los siguiente datos:\n"
                f"Amount: {money.amount} {money.currency}\n"
                f"Category: {response.payload.category}\n"
                f"Description: {response.payload.description}\n"
                f"MovementType: {response.payload.movement_type}"
            )
            _LOGGER.info("Sending message: %s", message_text)
            await evo_api.send_text_message(jid=jid, message=message_text)
    else:
        _LOGGER.error("Error desde n8n: %s", response.error_message)
        message.processing_result = aggregates.ProcessingResult(
            success=False,
            error_message=response.error_message
        )
        message_repo.save(new_item=message)
        await evo_api.send_text_message(jid=jid, message=response.error_message)

    return fastapi.Response(status_code=200)