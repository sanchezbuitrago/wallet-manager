import fastapi
import pydantic_settings

from app.commons import logs
from app.webhooks.commons.adapters import evolution_api
from app.webhooks.domain.model import commands
from app.webhooks.domain.services import whatsapp_events
from app.commons.adapters import mongo_uow

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
       uow=mongo_uow.MongoUOW()
   )
   return fastapi.Response(status_code=200)


@webhooks_routes.post("/n8n")
async def n8n_webhook(request: fastapi.Request) -> fastapi.Response:
    body = await request.json()
    _LOGGER.debug("n8n webhook body: %s", body)
    _LOGGER.debug("n8n webhook success: %s", body.get("success"))
    evo_api = evolution_api.DefaultEvolutionApiAdapter()
    if body.get("success") == "true":
        if body["payload"].get("error_message") is not None and body["payload"].get("error_message") != "":
            _LOGGER.error("Error en payload: %s", body["payload"].get("error_message"))
            await evo_api.send_text_message(jid=body["number"], message=body["payload"]["error_message"])
        else:
            amount = body["payload"]["monto"]
            category = body["payload"]["categoria"]
            description = body["payload"]["descripcion"]
            movement_type = body["payload"]["tipo"]
            message = f""" Se van a cargar los siguiente datos:\n monto: {amount},\n categoria: {category},\n descripcion: {description}, \n tipo: {movement_type}"""
            _LOGGER.info("Sending message: %s", message)
            await evo_api.send_text_message(
                jid=body["number"],
                message=message
            )
    else:
        await evo_api.send_text_message(jid=body["number"], message="No se pudo procesar el mensaje de manera correctamente. Intenta de nuevo")

    return fastapi.Response(status_code=200)