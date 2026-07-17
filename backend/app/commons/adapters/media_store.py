import abc
import base64
import os

import pydantic_settings

from app.commons import logs
from app.commons import standard_types

_LOGGER = logs.get_logger()


class UnsupportedMediaTypeError(Exception):
    ...


class _Settings(pydantic_settings.BaseSettings):
    media_storage_dir: str = "/app/storage/media"


_SETTINGS = _Settings()


class AbstractMediaAdapter(abc.ABC):
    """Base class for media storage adapters."""

    @abc.abstractmethod
    def save(self, base_64_content: str, mime_type: str) -> str:
        """Save base64-encoded media and return its URL path."""
        ...


class LocalMediaAdapter(AbstractMediaAdapter):
    """Media adapter that stores files on the local filesystem."""

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
        """Decode and store a base64-encoded media file.

        Args:
            base_64_content: The base64-encoded file content.
            mime_type: The MIME type of the media (e.g. ``audio/ogg``).

        Returns:
            The URL path to the saved file.

        Raises:
            UnsupportedMediaTypeError: If the MIME type is not supported.
        """
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
