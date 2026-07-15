import base64
import json
import decimal

import google.generativeai as genai

from app.commons import logs
from app.webhooks.commons.adapters.ai import base as ai_base

_LOGGER = logs.get_logger()

_AUDIO_ANALYSIS_PROMPT = """Eres el motor de Inteligencia Artificial para una aplicación de finanzas personales ("WalletManager"). Tu tarea consiste en escuchar el archivo de audio de WhatsApp adjunto y extraer la información financiera en un objeto JSON estricto.

⚠️ REGLA DE ORO (ANTI-ALUCINACIONES):
Antes de extraer nada, evalúa el audio. Si el audio está vacío, es puro silencio, es ininteligible, o NO contiene ninguna mención a dinero, gastos o ingresos, ESTÁ TOTALMENTE PROHIBIDO inventar o adivinar datos. En ese caso, debes ir directamente al ESCENARIO DE ERROR.

You MUST ONLY use the following CATEGORIES. No other categories are allowed:
- FOOD: Market, supermarket, groceries for home cooking
- DINING_OUT: Restaurants, fast food, deliveries, coffee shops
- TRANSPORTATION: Gas, tolls, parking, vehicle maintenance, SOAT, vehicle taxes
- ENTERTAINMENT: Movies, concerts, bars, nightclubs, social plans
- SPORTS: Gym, court rentals, referees, supplements, sportswear/equipment, tournament fees
- HEALTH: Doctor, insurance, pharmacy, medical exams
- SHOPPING: Clothing, electronics, non-essential purchases
- EDUCATION: Courses, books, learning platforms
- HOME: Rent, utilities, internet, cleaning supplies, property taxes, home maintenance
- SALARY: Payroll income
- FREELANCE: Independent work income
- INVESTMENTS: Profits or investments in different platforms or actives
- OTHER: Anything that does not fit in the above

RESPONSE STRUCTURE:
{
  "success": true/false,
  "payload": {
    "amount": <float or int, 0 on error>,
    "category": "<One of the categories above in UPPERCASE, or '' on error>",
    "description": "<text in Spanish, or '' on error>",
    "movement_type": "<'INCOME' or 'EXPENSE', or '' on error>"
  },
  "error_message": "<filled only when success=false, otherwise ''>"
}

PARAMETERS TO EXTRACT:
1. "amount": The numeric total value (float or int). On error, set to 0.
2. "category": Must be EXACTLY one of the categories listed above, in UPPERCASE. On error, set to "".
3. "description": Brief summary in Spanish of what was spent or received (e.g., "Compra de comida", "Pago de nómina", "Alquiler de cancha de fútbol"). On error, set to "".
4. "movement_type": Must be exactly "INCOME" or "EXPENSE". On error, set to "".
5. "error_message" (only when success=false): Describe the specific problem in Spanish:
   - Audio vacío o silencio: "El audio está vacío o es solo silencio. Por favor graba un mensaje indicando el monto y el concepto."
   - Sin información financiera: "No detecté información sobre dinero, gastos o ingresos en el audio. Por favor indica el monto y en qué lo gastaste o recibiste."
   - Monto no detectable: "Escuché el concepto pero no logré identificar un monto válido. Por favor repite el mensaje indicando claramente el valor numérico."
   - Concepto no claro: "Identifiqué un monto pero no quedó claro el concepto o categoría. Por favor proporciona más detalles sobre este movimiento."
   - Audio ininteligible: "El audio no es claro o tiene mucho ruido. Por favor graba nuevamente el mensaje en un lugar más silencioso."

STRICT FORMATTING RULES:
- Return ONLY the JSON object.
- NO markdown code blocks (like ```json).
- NO words before or after the braces.

--- EXAMPLE 1: SUCCESSFUL SCENARIO ---
Audio: "Compré el mercado de la semana, fueron 150 mil pesos"
{
  "success": true,
  "payload": {
    "amount": 150000,
    "category": "FOOD",
    "description": "Compré el mercado de la semana",
    "movement_type": "EXPENSE"
  },
  "error_message": ""
}

--- EXAMPLE 2: ERROR SCENARIO (Silence) ---
{
  "success": false,
  "payload": {
    "amount": 0,
    "category": "",
    "description": "",
    "movement_type": ""
  },
  "error_message": "El audio está vacío o es solo silencio. Por favor graba un mensaje indicando el monto y el concepto."
}"""


class GeminiAIAdapter(ai_base.AIAdapter):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        _LOGGER.info("GeminiAIAdapter initialized with model: %s", model)

    async def analyze_audio(self, audio_base64: str, mime_type: str) -> ai_base.AnalyzeAudioResult:
        try:
            _LOGGER.info("Analyzing audio with Gemini (mime_type: %s)", mime_type)

            audio_data = base64.b64decode(audio_base64)

            response = await self._model.generate_content_async([
                _AUDIO_ANALYSIS_PROMPT,
                {"mime_type": mime_type, "data": audio_data}
            ])

            raw_text = response.text.strip()
            _LOGGER.debug("Gemini raw response: %s", raw_text)

            if raw_text.startswith("```"):
                raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

            data = json.loads(raw_text)

            if data.get("success") is False:
                return ai_base.AnalyzeAudioResult(
                    success=False,
                    error_message=data.get("error_message", "Error desconocido al procesar el audio")
                )

            payload = data.get("payload", data)

            amount = payload.get("amount")
            if amount is not None:
                amount = decimal.Decimal(str(amount))

            return ai_base.AnalyzeAudioResult(
                success=True,
                amount=amount,
                category=payload.get("category", ""),
                description=payload.get("description", ""),
                movement_type=payload.get("movement_type", "")
            )

        except json.JSONDecodeError as e:
            _LOGGER.error("Failed to parse Gemini response as JSON: %s", str(e))
            return ai_base.AnalyzeAudioResult(
                success=False,
                error_message="No se pudo interpretar la respuesta del audio"
            )
        except Exception as e:
            _LOGGER.error("Error analyzing audio with Gemini: %s", str(e))
            return ai_base.AnalyzeAudioResult(
                success=False,
                error_message="Ocurrió un error al procesar tu audio. Por favor intenta de nuevo."
            )
