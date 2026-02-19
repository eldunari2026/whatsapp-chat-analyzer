"""Ollama LLM client for text and vision inference."""

from __future__ import annotations

import logging

from whatsapp_analyzer.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class OllamaClient(BaseLLMClient):
    """LLM client wrapping the Ollama Python SDK."""

    def __init__(
        self,
        model: str = "llama3.1:8b",
        host: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.host = host
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import ollama
            self._client = ollama.Client(host=self.host)
        return self._client

    def generate(self, prompt: str) -> str:
        """Generate text using the configured Ollama model."""
        try:
            response = self.client.generate(model=self.model, prompt=prompt)
            # Handle both dict and Pydantic model responses
            if hasattr(response, "response"):
                return response.response.strip()
            return response.get("response", "").strip()
        except Exception as e:
            logger.error("Ollama generation failed: %s", e)
            raise RuntimeError(
                f"Failed to generate response from Ollama ({self.model}): {e}"
            ) from e

    def is_available(self) -> bool:
        """Check if Ollama server is reachable and model is available."""
        try:
            result = self.client.list()
            # Handle both Pydantic model and dict responses
            if hasattr(result, "models"):
                models = result.models
            else:
                models = result.get("models", [])
            for m in models:
                name = m.model if hasattr(m, "model") else m.get("name", "")
                if self.model in name:
                    return True
            return False
        except Exception:
            return False
