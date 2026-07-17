import abc
import httpx

import pydantic
import pydantic_settings
from app.commons import base_types
from app.commons import logs

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
    """Create an async HTTP client configured for the Evolution API."""
    return httpx.AsyncClient(
        base_url=url,
        headers={
            "apikey": f"{api_key}",
            "Content-Type": "application/json"
        },
        timeout=10.0
    )


class EvolutionApiAdapter(abc.ABC):
    """Abstract adapter for the Evolution WhatsApp API."""

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
    """Default implementation of the Evolution API adapter."""

    async def get_profile(self, jid: str) -> None:
        """Fetch a WhatsApp profile and resolve the real JID.

        Args:
            jid: The WhatsApp JID to resolve.

        Returns:
            The resolved JID string, or None if not found.
        """
        payload = {
            "number": jid
        }

        try:
            http_client = get_http_client(
                _SETTINGS.evolution_api_url,
                _SETTINGS.evolution_api_key,
            )
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
                resolved_jid = data.get("id") or data.get("wuid")
                _LOGGER.debug("Resolved number: %s", resolved_jid)
                if resolved_jid and "@s.whatsapp.net" in resolved_jid:
                    return resolved_jid

        except Exception as e:
            _LOGGER.error("Error resolving LID %s: %s", jid, e)

    async def send_text_message(self, jid: str, message: str) -> None:
        """Send a text message via the Evolution API."""
        _LOGGER.info("Sending text message to %s", jid)
        payload = {
            "number": jid,
            "text": message
        }
        _LOGGER.debug("Message payload: %s", payload)
        http_client = get_http_client(
            url=_SETTINGS.evolution_api_url,
            api_key=_SETTINGS.evolution_api_key,
        )
        response = await http_client.post(_SEND_MESSAGE_RESOURCE, json=payload)
        _LOGGER.debug("Send message status: %s", response.status_code)
        _LOGGER.debug("Send message response: %s", response.text)

    async def get_media_file(self, message_id: str) -> MediaFile:
        """Download a media file from a WhatsApp message.

        Args:
            message_id: The WhatsApp message ID containing the media.

        Returns:
            A MediaFile with the base64-encoded content.

        Raises:
            ErrorGettingMediaFileException: If the download fails.
        """
        http_client = get_http_client(
            _SETTINGS.evolution_api_url,
            _SETTINGS.evolution_api_key,
        )
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
