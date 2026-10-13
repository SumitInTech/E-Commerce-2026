"""
Large Language Model Adapter.
Implements AbstractLLMProvider with support for Google Gemini API via async httpx,
and includes a robust deterministic synthesis fallback for offline/development mode.
"""
from typing import Optional
import httpx
import logging

from core.interfaces.llm_provider import AbstractLLMProvider
from core.config import settings

logger = logging.getLogger(__name__)


class GeminiLLMProvider(AbstractLLMProvider):
    """
    Google Gemini REST API adapter.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )

    async def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Sends prompt to Gemini API. If API key is absent or request fails,
        falls back gracefully to deterministic context extraction.
        """
        if not self.api_key:
            return self._deterministic_fallback(prompt, system_instruction)

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.endpoint}?key={self.api_key}",
                    headers=headers,
                    json=payload
                )
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()

                logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
                return self._deterministic_fallback(prompt, system_instruction)

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            return self._deterministic_fallback(prompt, system_instruction)

    def _deterministic_fallback(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Deterministic synthesis when external LLM API is unavailable.
        Extracts relevant information from the injected prompt context.
        """
        if "CONTEXT:" in prompt:
            context_part = prompt.split("CONTEXT:")[-1].split("USER QUERY:")[0].strip()
            # Clean up into readable bullet points
            lines = [l.strip() for l in context_part.split("\n") if l.strip() and not l.startswith("#")]
            summary = "\n".join(lines[:6])
            return (
                f"[Stylist Knowledge Assistant]: Based on our store policy and sizing specifications:\n\n"
                f"{summary}\n\n"
                f"If you have further questions, our human styling support is available 24/7."
            )
        return (
            "[Stylist Knowledge Assistant]: Thank you for reaching out! "
            "For detailed guidance on garment sizing, care recommendations, and return policies, "
            "please consult our sizing guidelines or contact our support team."
        )
