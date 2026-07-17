import fastapi

from app.commons.adapters import mongo_uow
from app.webhooks.domain.model import commands
from app.webhooks.domain.services import message_handler

webhooks_routes = fastapi.APIRouter()


@webhooks_routes.post("/whatsapp")
async def whatsapp_webhook(request: fastapi.Request) -> fastapi.Response:
    """Handle incoming WhatsApp webhook events from Evolution API."""
    body = await request.json()
    cmd = commands.WhatsappEventCommand.model_validate(body)
    if cmd.event == "messages.upsert":
        uow = mongo_uow.MongoUOW()
        await message_handler.process(cmd, uow)
    return fastapi.Response(status_code=200)
