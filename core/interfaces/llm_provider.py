"""
Abstract Base Class for Large Language Model Providers.
Enables seamless polymorphic substitution between Gemini, OpenAI, Claude, or local offline mock.
"""
from abc import ABC, abstractmethod
from typing import Optional


class AbstractLLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Asynchronously generates a natural language response given a user prompt and optional system context.
        """
        pass
