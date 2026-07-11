import abc
import base64
import os

import pydantic_settings

from app.commons import logs, standard_types

_LOGGER = logs.get_logger()


class UnsupportedMediaTypeError(Exception):
    ...


class _Settings(pydantic_settings.BaseSettings):
    media_storage_dir: str = "/app/storage/media"


_SETTINGS = _Settings()


class AbstractMediaAdapter(abc.ABC):
    @abc.abstractmethod
    def save(self, base_64_content: str, mime_type: str) -> str:
        ...


class LocalMediaAdapter(AbstractMediaAdapter):
    _MIME_MAP: dict[str, tuple[str, str]] = {
        "audio/ogg": ("audio", ".ogg"),
        "audio/mpeg": ("audio", ".mp3"),
        "audio/mp4": ("audio", ".m4a"),
        "audio/wav": ("audio", ".wav"),
        "image/jpeg": ("image", ".jpg"),
        "image/png": ("image", ".png"),
        "image/webp": ("image", ".webp"),
        "video/mp4": ("video", ".mp4"),
        "video/ogg": ("video", ".ogv"),
        "video/webm": ("video", ".webm"),
    }

    def save(self, base_64_content: str, mime_type: str) -> str:
        base_type = mime_type.split(";")[0].strip()
        _LOGGER.info("Saving media with mime type %s", mime_type)

        entry = self._MIME_MAP.get(base_type)
        if not entry:
            raise UnsupportedMediaTypeError(f"Unsupported mime type: {mime_type}")

        subdir, ext = entry
        filename = f"{standard_types.IdGenerator.generate(length=20)}{ext}"
        relative_path = os.path.join(subdir, filename)
        full_path = os.path.join(_SETTINGS.media_storage_dir, subdir, filename)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(base64.b64decode(base_64_content))

        url = f"/static/media/{relative_path}"
        _LOGGER.info("Media saved at %s", url)
        return url
