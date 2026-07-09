import abc
import httpx
from typing import Any

from pydantic_settings import BaseSettings

from app.webhooks.commons.adapters.n8n.domain import model

class _Settings(BaseSettings):
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
            print("Calling n8n")
            response = await self.http_client.post(url="", json=message.model_dump_json())
            print(response.text)
            response.raise_for_status()
        except Exception as e:
            print(str(e))
