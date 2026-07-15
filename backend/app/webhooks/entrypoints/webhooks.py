import fastapi
import pydantic_settings

from app.commons import logs
from app.commons.adapters import media_store
from app.commons.adapters import mongo_uow
from app.webhooks.commons.adapters import evolution_api
from app.webhooks.commons.adapters import ai
from app.webhooks.domain.model import commands
from app.webhooks.domain.services import whatsapp_events

_LOGGER = logs.get_logger()

webhooks_routes = fastapi.APIRouter()


class _Settings(pydantic_settings.BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"


_SETTINGS = _Settings()


@webhooks_routes.post("/whatsapp")
async def whatsapp_webhook(request: fastapi.Request) -> fastapi.Response:
    body = await request.json()
    _LOGGER.debug("WhatsApp webhook body: %s", body)

    cmd = commands.WhatsappEventCommand.model_validate(body)
    await whatsapp_events.process_event(
        cmd=cmd,
        evolution_api_adapter=evolution_api.DefaultEvolutionApiAdapter(),
        uow=mongo_uow.MongoUOW(),
        media_adapter=media_store.LocalMediaAdapter(),
        ai_adapter=ai.GeminiAIAdapter(
            api_key=_SETTINGS.gemini_api_key,
            model=_SETTINGS.gemini_model
        )
    )
    return fastapi.Response(status_code=200)
