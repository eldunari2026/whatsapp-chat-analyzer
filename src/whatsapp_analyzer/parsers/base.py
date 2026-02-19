"""Abstract base parser for WhatsApp chat data."""

from abc import ABC, abstractmethod

from whatsapp_analyzer.models.message import Conversation


class BaseParser(ABC):
    """Base class for all chat parsers."""

    @abstractmethod
    def parse(self, source: str) -> Conversation:
        """Parse the given source and return a Conversation.

        Args:
            source: File path or raw text depending on the parser.

        Returns:
            A Conversation object with parsed messages.
        """

    @abstractmethod
    def can_handle(self, source: str) -> bool:
        """Check if this parser can handle the given source.

        Args:
            source: File path or raw text.

        Returns:
            True if this parser can handle the source.
        """
