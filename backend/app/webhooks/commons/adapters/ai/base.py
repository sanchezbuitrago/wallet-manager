import abc
import decimal

from app.commons import base_types


class AnalyzeAudioResult(base_types.ValueObject):
    success: bool
    amount: decimal.Decimal | None = None
    category: str | None = None
    description: str | None = None
    movement_type: str | None = None
    error_message: str = ""


class AIAdapter(abc.ABC):
    @abc.abstractmethod
    async def analyze_audio(self, audio_base64: str, mime_type: str) -> AnalyzeAudioResult:
        ...
