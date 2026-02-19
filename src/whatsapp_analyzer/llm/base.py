"""Abstract base class for LLM clients."""

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Base class for LLM inference clients."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a text response from the LLM.

        Args:
            prompt: The input prompt.

        Returns:
            The generated text response.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM backend is reachable."""
