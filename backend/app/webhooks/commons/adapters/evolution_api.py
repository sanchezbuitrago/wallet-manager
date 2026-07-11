import abc
import httpx

import pydantic
import pydantic_settings
from app.commons import base_types, logs

_LOGGER = logs.get_logger()


class _Settings(pydantic_settings.BaseSettings):
    evolution_api_key: str
    evolution_api_url: str
    evolution_instance: str


_SETTINGS = _Settings()

_GET_PROFILE_RESOURCE = f"/chat/fetchProfile/{_SETTINGS.evolution_instance}"
_SEND_MESSAGE_RESOURCE = f"/message/sendText/{_SETTINGS.evolution_instance}"
_GET_MEDIA_FILE_RESOURCE = f"/chat/getBase64FromMediaMessage/{_SETTINGS.evolution_instance}"

class ErrorGettingMediaFileException(Exception):
    ...

class MediaFile(base_types.ValueObject):
    media_type: str = pydantic.Field(alias="mediaType")
    file_name: str = pydantic.Field(alias="fileName")
    mimetype: str
    base_64: str = pydantic.Field(alias="base64")


def get_http_client(url: str, api_key: str) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=url,
        headers={
            "apikey": f"{api_key}",
            "Content-Type": "application/json"
        },
        timeout=10.0
    )


class EvolutionApiAdapter(abc.ABC):
    @abc.abstractmethod
    async def get_profile(self, jid: str) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def send_text_message(self, jid: str, message: str) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_media_file(self, message_id: str) -> MediaFile:
        raise NotImplementedError()


class DefaultEvolutionApiAdapter(EvolutionApiAdapter):
    async def get_profile(self, jid: str) -> None:
        payload = {
            "number": jid
        }

        try:
            http_client = get_http_client(_SETTINGS.evolution_api_url, _SETTINGS.evolution_api_key)
            response = await http_client.post(
                url=_GET_PROFILE_RESOURCE,
                json=payload,
            )
            _LOGGER.info("Fetching profile for %s", jid)
            _LOGGER.debug("Profile response: %s", response)
            _LOGGER.debug("Profile body: %s", response.text)
            if response.status_code == 200:
                data = response.json()
                _LOGGER.debug("Profile data: %s", data)
                numero_real = data.get("id") or data.get("wuid")
                _LOGGER.debug("Resolved number: %s", numero_real)
                if numero_real and "@s.whatsapp.net" in numero_real:
                    return numero_real

        except Exception as e:
            _LOGGER.error("Error al resolver el LID %s: %s", jid, e)

    async def send_text_message(self, jid: str, message: str) -> None:
        _LOGGER.info("Sending text message to %s", jid)
        payload = {
            "number": jid,
            "text": message
        }
        _LOGGER.debug("Message payload: %s", payload)
        http_client = get_http_client(url=_SETTINGS.evolution_api_url, api_key=_SETTINGS.evolution_api_key)
        response = await http_client.post(_SEND_MESSAGE_RESOURCE, json=payload)
        _LOGGER.debug("Send message status: %s", response.status_code)
        _LOGGER.debug("Send message response: %s", response.text)

    async def get_media_file(self, message_id: str) -> MediaFile:
        http_client = get_http_client(_SETTINGS.evolution_api_url, _SETTINGS.evolution_api_key)
        response = await http_client.post(_GET_MEDIA_FILE_RESOURCE, json={
            "message": {
                "key": {
                    "id": message_id
                }
            }
        })

        if response.status_code == 201:
            _LOGGER.debug("Media file response: %s", response.text)
            return MediaFile(**response.json())

        raise ErrorGettingMediaFileException()
