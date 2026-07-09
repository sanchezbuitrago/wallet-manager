import abc
import httpx

import pydantic
from app.commons import base_types

_API_KEY = "4CEDBD17D969-40FD-BC87-2D60E17C9D8A"
_EVOLUTION_API_URL = "http://evolution-api:8080"
_INSTANCE_NAME = "WalletManager"
_GET_PROFILE_RESOURCE = f"/chat/fetchProfile/{_INSTANCE_NAME}"
_SEND_MESSAGE_RESOURCE = f"/message/sendText/{_INSTANCE_NAME}"
_GET_MEDIA_FILE_RESOURCE = f"/chat/getBase64FromMediaMessage/{_INSTANCE_NAME}"

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
            http_client = get_http_client(_EVOLUTION_API_URL, _API_KEY)
            response = await http_client.post(
                url=_GET_PROFILE_RESOURCE,
                json=payload,
            )
            print("Profile ----------------")
            print(response)
            print(response.text)
            if response.status_code == 200:
                data = response.json()
                print(data)
                numero_real = data.get("id") or data.get("wuid")
                print(numero_real)
                if numero_real and "@s.whatsapp.net" in numero_real:
                    return numero_real

        except Exception as e:
            print(f"Error al resolver el LID {jid}: {e}")

    async def send_text_message(self, jid: str, message: str) -> None:
        print("Sending text message ------------------------")
        payload = {
            "number": jid,
            "text": message
        }
        print(payload)
        http_client = get_http_client(url=_EVOLUTION_API_URL, api_key=_API_KEY)
        response = await http_client.post(_SEND_MESSAGE_RESOURCE, json=payload)
        print(response.status_code)
        print(response.text)

    async def get_media_file(self, message_id: str) -> MediaFile:
        http_client = get_http_client(_EVOLUTION_API_URL, _API_KEY)
        response = await http_client.post(_GET_MEDIA_FILE_RESOURCE, json={
            "message": {
                "key": {
                    "id": message_id
                }
            }
        })

        if response.status_code == 201:
            print(response.text)
            return MediaFile(**response.json())

        raise ErrorGettingMediaFileException()
