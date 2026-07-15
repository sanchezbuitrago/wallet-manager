from app.webhooks.commons.adapters.ai import base
from app.webhooks.commons.adapters.ai import gemini

AIAdapter = base.AIAdapter
AnalyzeAudioResult = base.AnalyzeAudioResult
GeminiAIAdapter = gemini.GeminiAIAdapter

__all__ = ["AIAdapter", "AnalyzeAudioResult", "GeminiAIAdapter"]
