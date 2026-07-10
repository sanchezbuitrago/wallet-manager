import abc
import httpx

import pydantic_settings

from app.commons import logs
from app.webhooks.commons.adapters.n8n.domain import model

_LOGGER = logs.get_logger()

class _Settings(pydantic_settings.BaseSettings):
    n8n_webhook: str


def get_http_client(url: str) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=url,
        headers={
            "Content-Type": "application/json"
        },
        timeout=10.0
    )


class N8NAdapter(abc.ABC):
    @abc.abstractmethod
    def send_message_to_webhook(self, message: model.N8NMediaFile) -> None:
        pass

class DefaultN8NAdapter(N8NAdapter):
    def __init__(self):
        self.settings = _Settings()
        self.http_client = get_http_client(self.settings.n8n_webhook)

    async def send_message_to_webhook(self, message: model.N8NMediaFile) -> None:
        try:
            _LOGGER.info("Calling n8n webhook")
            response = await self.http_client.post(url="", json=message.model_dump_json())
            _LOGGER.debug("n8n response: %s", response.text)
            response.raise_for_status()
        except Exception as e:
            _LOGGER.error("Error calling n8n: %s", str(e))
